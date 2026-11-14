#include "pch.h" // Replace with stdafx.h if needed.
#include "GtMotionController.h"
#include <math.h>
#include <new>
#include <wchar.h>

#pragma comment(lib, "gts.lib")

namespace
{
    const double kMaxSpeedPulsePerMs = 20.0; // UI guard only; set to your proven machine limit.
    const DWORD kPointTimeoutMs = 60000;
    const DWORD kStartTimeoutMs = 1200;
    const DWORD kStopWaitTimeoutMs = 10000;
    const DWORD kJogWatchdogMs = 30000;
    const DWORD kHomeTimeoutMs = 120000;
    const double kPositionTolerance = 1.0;

    // GTS status bit definitions commonly documented for GTS basic API:
    // bit 1 drive alarm, bit 5 positive limit, bit 6 negative limit,
    // bit 8 stop-IO/estop, bit 9 servo enabled, bit 10 planned motion.
    // Verify against the exact manual/header supplied with your GTS-800-PG.
    const long STS_DRIVE_ALARM = 0x0002;
    const long STS_POS_LIMIT   = 0x0020;
    const long STS_NEG_LIMIT   = 0x0040;
    const long STS_ESTOP_IO    = 0x0100;
    const long STS_SERVO_ON    = 0x0200;
    const long STS_MOVING      = 0x0400;

    long AxisMask(short axis) { return 1L << (axis - 1); }
}

CGtMotionController::CGtMotionController()
    : m_opened(false), m_initialized(false), m_extensionReady(false),
      m_safetyTripped(false), m_safetySource(GTS_SAFETY_NONE), m_lightCurtainActiveHigh(true),
      m_stopInputActiveHigh(true), m_notifyHwnd(NULL)
{
    for (int i = 0; i < 4; ++i)
    {
        m_axisEnabled[i] = false;
        m_axisHomed[i] = false;
    }
    m_axisForXyz[0] = 1;
    m_axisForXyz[1] = 2;
    m_axisForXyz[2] = 3;
}

void CGtMotionController::Log(const wchar_t* text) const
{
    if (!m_notifyHwnd || !text) return;
    const size_t len = wcslen(text);
    wchar_t* copy = new (std::nothrow) wchar_t[len + 1];
    if (!copy) return;
    wcscpy_s(copy, len + 1, text);
    if (!::PostMessageW(m_notifyHwnd, WM_GTS_MOTION_LOG, 0,
                        reinterpret_cast<LPARAM>(copy)))
        delete[] copy;
}

void CGtMotionController::LogResult(const wchar_t* name, short rc) const
{
    wchar_t buffer[256] = {};
    _snwprintf_s(buffer, _countof(buffer), _TRUNCATE, L"%s 返回值：%d", name, (int)rc);
    Log(buffer);
}

short CGtMotionController::Initialize(HWND notifyHwnd,
                                     bool lightCurtainActiveHigh,
                                     bool stopInputActiveHigh)
{
    m_notifyHwnd = notifyHwnd;
    SetSafetyInputPolarity(lightCurtainActiveHigh, stopInputActiveHigh);
    if (m_initialized)
    {
        Log(L"控制器已经初始化。");
        return 0;
    }

    short rc;
    if (!m_opened)
    {
        rc = GT_Open();
        LogResult(L"GT_Open", rc);
        if (rc != 0) return rc;
        m_opened = true;
    }

    rc = GT_Reset();
    LogResult(L"GT_Reset", rc);
    if (rc != 0) return rc;

    // Ensure GTS800.cfg is in the process working directory.
    char cfg[] = "GTS800.cfg";
    rc = GT_LoadConfig(cfg);
    LogResult(L"GT_LoadConfig", rc);
    if (rc != 0) return rc;

    // This clears controller status flags for axes 1..3; it does not fix a real
    // alarm or limit input. Do not continue if it fails.
    rc = GT_ClrSts(1, 3);
    LogResult(L"GT_ClrSts(1, 3)", rc);
    if (rc != 0) return rc;

    char extCfg[] = "ExtMdl.cfg";
    rc = GT_OpenExtMdl(NULL);
    LogResult(L"GT_OpenExtMdl", rc);
    if (rc == 0)
    {
        short extRc = GT_LoadExtConfig(extCfg);
        LogResult(L"GT_LoadExtConfig(ExtMdl.cfg)", extRc);
        m_extensionReady = extRc == 0;
        if (!m_extensionReady) GT_CloseExtMdl();
    }
    else
    {
        Log(L"gLink200 扩展模块未就绪；轴控仍可使用，扩展 IO 和依赖它的流程已禁用。");
    }

    m_initialized = true;
    Log(m_extensionReady
        ? L"初始化完成，控制器与 gLink200 已就绪。请确认实际报警、限位和急停后再使能伺服。"
        : L"控制器初始化完成；gLink200 不可用，扩展 IO 与依赖它的流程已禁用。");
    return 0;
}

void CGtMotionController::SetSafetyInputPolarity(bool lightCurtainActiveHigh,
                                                  bool stopInputActiveHigh)
{
    m_lightCurtainActiveHigh = lightCurtainActiveHigh;
    m_stopInputActiveHigh = stopInputActiveHigh;
}

short CGtMotionController::ApplySafetyInputPolarity(bool lightCurtainActiveHigh,
                                                     bool stopInputActiveHigh)
{
    if (!m_initialized) return -103;
    for (short axis = 1; axis <= 3; ++axis)
    {
        long status = 0;
        short rc = GT_GetSts(axis, &status);
        if (rc != 0) return rc;
        if ((status & STS_MOVING) != 0) return -132;
        if ((status & STS_SERVO_ON) != 0 || m_axisEnabled[axis]) return -117;
    }
    SetSafetyInputPolarity(lightCurtainActiveHigh, stopInputActiveHigh);
    wchar_t text[192] = {};
    _snwprintf_s(text, _countof(text), _TRUNCATE,
        L"安全输入极性已应用：EXI4=%s有效，EXI1=%s有效。应用不会清除联锁；请读取输入后显式清报警。",
        lightCurtainActiveHigh ? L"高电平" : L"低电平",
        stopInputActiveHigh ? L"高电平" : L"低电平");
    Log(text);
    return 0;
}

bool CGtMotionController::IsAxisHomed(short axis) const
{
    return axis >= 1 && axis <= 3 && m_axisHomed[axis];
}

bool CGtMotionController::SetCoordinateMapping(const short axisForXyz[3])
{
    if (!axisForXyz) return false;
    bool seen[4] = {};
    for (int i = 0; i < 3; ++i)
    {
        const short axis = axisForXyz[i];
        if (axis < 1 || axis > 3 || seen[axis]) return false;
        seen[axis] = true;
    }
    for (int i = 0; i < 3; ++i) m_axisForXyz[i] = axisForXyz[i];
    return true;
}

short CGtMotionController::EnableAxes()
{
    if (!m_initialized) return -101;
    for (short axis = 1; axis <= 3; ++axis)
    {
        if (m_axisEnabled[axis]) continue;
        short rc = GT_AxisOn(axis);
        LogResult(L"GT_AxisOn", rc);
        if (rc != 0)
        {
            Log(L"伺服使能失败。请检查驱动报警、限位配置和接线。");
            return rc;
        }
        m_axisEnabled[axis] = true;
        Sleep(150);
    }
    Log(L"三轴伺服使能指令均已返回成功。");
    return 0;
}

short CGtMotionController::DisableAxes()
{
    short firstError = 0;
    for (short axis = 1; axis <= 3; ++axis)
    {
        if (!m_axisEnabled[axis]) continue;
        short rc = GT_AxisOff(axis);
        LogResult(L"GT_AxisOff", rc);
        if (rc == 0) m_axisEnabled[axis] = false;
        else if (firstError == 0) firstError = rc;
    }
    return firstError;
}

short CGtMotionController::CheckCanMove(short axis, int direction,
                                         bool allowRetreatFromLimit) const
{
    if (!m_initialized || !m_opened) return -101;
    if (axis < 1 || axis > 3) return -100;
    if (!m_axisEnabled[axis]) return -102;

    long sts = 0;
    short rc = GT_GetSts(axis, &sts);
    if (rc != 0) return rc;

    if (sts & STS_DRIVE_ALARM) return -110;
    if (sts & STS_ESTOP_IO) return -111;

    const bool posLimit = (sts & STS_POS_LIMIT) != 0;
    const bool negLimit = (sts & STS_NEG_LIMIT) != 0;

    if (!allowRetreatFromLimit && (posLimit || negLimit)) return -112;
    if (allowRetreatFromLimit)
    {
        if (posLimit && negLimit) return -113; // both limits active: don't guess direction
        if (posLimit && direction > 0) return -114; // don't jog further into positive limit
        if (negLimit && direction < 0) return -115; // don't jog further into negative limit
    }
    return 0;
}

short CGtMotionController::StopAndWait(long mask, DWORD timeoutMs)
{
    // GTS standard API: option 0 is commonly used for smooth stop; verify your SDK.
    short rc = GT_Stop(mask, 0);
    LogResult(L"GT_Stop(mask, 0)", rc);
    if (rc != 0) return rc;

    DWORD begin = GetTickCount();
    while (GetTickCount() - begin < timeoutMs)
    {
        bool stopped = true;
        for (short axis = 1; axis <= 3; ++axis)
        {
            if ((mask & AxisMask(axis)) == 0) continue;
            long sts = 0;
            rc = GT_GetSts(axis, &sts);
            if (rc != 0) return rc;
            if (sts & STS_MOVING) stopped = false;
        }
        if (stopped) return 0;
        Sleep(10);
    }
    Log(L"等待轴停止超时。请使用硬件急停并检查设备状态。");
    return -104;
}

short CGtMotionController::ReadDigitalInputs(long& inputs) const
{
    inputs = 0;
    short rc = GT_GetDi(MC_GPI, &inputs);
    if (rc != 0) LogResult(L"GT_GetDi(MC_GPI)", rc);
    return rc;
}

short CGtMotionController::SetDirectOutput(short index, bool value)
{
    // The course IO table labels outputs EXO0..EXO10, while the GTS SDK API
    // numbers doIndex from 1. Keep callers in physical channel numbering.
    const short sdkIndex = (short)(index + 1);
    short rc = (index < 0 || index > 15) ? 7
        : GT_SetDoBit(MC_GPO, sdkIndex, value ? 1 : 0);
    wchar_t text[160] = {};
    _snwprintf_s(text, _countof(text), _TRUNCATE,
        L"GT_SetDoBit(MC_GPO, EXO%d -> doIndex=%d) 返回值：%d",
        (int)index, (int)sdkIndex, (int)rc);
    Log(text);
    return rc;
}

short CGtMotionController::SetExtensionOutput(short index, bool value)
{
    if (!m_extensionReady) return -130;
    short rc = GT_SetExtIoBit(0, index, value ? 1 : 0);
    if (rc != 0) LogResult(L"GT_SetExtIoBit", rc);
    return rc;
}

short CGtMotionController::CheckSafety(volatile LONG* stopRequested)
{
    if (m_safetyTripped)
    {
        if (stopRequested) InterlockedExchange(stopRequested, 1);
        return -116;
    }

    long inputs = 0;
    short rc = ReadDigitalInputs(inputs);
    if (rc != 0) return rc;

    const bool lightBit = ((inputs >> 4) & 1) != 0; // EXI4: light curtain
    const bool stopBit = ((inputs >> 1) & 1) != 0;  // EXI1: system stop
    const bool lightActive = lightBit == m_lightCurtainActiveHigh;
    const bool stopActive = stopBit == m_stopInputActiveHigh;
    if (!lightActive && !stopActive) return 0;

    m_safetyTripped = true;
    m_safetySource = (lightActive ? GTS_SAFETY_LIGHT_CURTAIN : GTS_SAFETY_NONE) |
                     (stopActive ? GTS_SAFETY_SYSTEM_STOP : GTS_SAFETY_NONE);
    if (stopRequested) InterlockedExchange(stopRequested, 1);
    Log(lightActive
        ? L"检测到光幕输入触发：请求停止三轴、关闭绿灯并打开红灯/蜂鸣器；气缸保持当前输出。"
        : L"检测到系统停止输入：请求停止三轴、关闭绿灯并打开红灯/蜂鸣器；气缸保持当前输出。");
    StopAndWait(0x7, kStopWaitTimeoutMs);
    SetDirectOutput(2, false);
    SetDirectOutput(0, true);
    SetDirectOutput(3, true);
    return -116;
}

short CGtMotionController::SetLogicalOutput(int output, bool on,
                                             const bool extendLevelHigh[4])
{
    short safetyRc = CheckSafety(NULL);
    if (safetyRc != 0) return safetyRc;
    short rc = 0;
    switch (output)
    {
    case GTS_OUT_RED:         return SetDirectOutput(0, on);
    case GTS_OUT_YELLOW:      return SetDirectOutput(1, on);
    case GTS_OUT_GREEN:       return SetDirectOutput(2, on);
    case GTS_OUT_BUZZER:      return SetDirectOutput(3, on);
    case GTS_OUT_SCREWDRIVER: return SetDirectOutput(7, on);
    case GTS_OUT_GRIPPER:     return SetDirectOutput(8, on);
    case GTS_OUT_VACUUM:      return SetDirectOutput(9, on);
    case GTS_OUT_PRESS_CYLINDER:
    {
        const bool highMeansExtend = !extendLevelHigh || extendLevelHigh[0];
        return SetDirectOutput(10, on ? highMeansExtend : !highMeansExtend);
    }
    case GTS_OUT_RODLESS:
    case GTS_OUT_BIN2:
    case GTS_OUT_BIN3:
    {
        if (!extendLevelHigh) return -103;
        const int i = output == GTS_OUT_RODLESS ? 1 : (output == GTS_OUT_BIN2 ? 2 : 3);
        const short index = output == GTS_OUT_RODLESS ? 0 : (output == GTS_OUT_BIN2 ? 1 : 2);
        return SetExtensionOutput(index, on ? extendLevelHigh[i] : !extendLevelHigh[i]);
    }
    default:
        rc = -103;
        break;
    }
    return rc;
}

short CGtMotionController::ResetMachineOutputs(const bool extendLevelHigh[4],
                                               const bool resetExtend[4],
                                               bool polarityConfirmed)
{
    if (!polarityConfirmed || !extendLevelHigh || !resetExtend) return -131;
    if (!m_extensionReady) return -130;

    short firstError = 0;
    const int directOutputs[] = { GTS_OUT_RED, GTS_OUT_YELLOW, GTS_OUT_GREEN,
                                  GTS_OUT_BUZZER, GTS_OUT_SCREWDRIVER,
                                  GTS_OUT_GRIPPER, GTS_OUT_VACUUM };
    for (size_t i = 0; i < _countof(directOutputs); ++i)
    {
        short rc = SetLogicalOutput(directOutputs[i], false, extendLevelHigh);
        if (firstError == 0 && rc != 0) firstError = rc;
    }
    const int cylinders[] = { GTS_OUT_PRESS_CYLINDER, GTS_OUT_RODLESS,
                              GTS_OUT_BIN2, GTS_OUT_BIN3 };
    for (size_t i = 0; i < _countof(cylinders); ++i)
    {
        short rc = SetLogicalOutput(cylinders[i], resetExtend[i], extendLevelHigh);
        if (firstError == 0 && rc != 0) firstError = rc;
    }
    if (firstError == 0)
        Log(L"复位输出指令已发送：灯/蜂鸣器关闭，气缸按逐路配置的目标状态动作。无独立行程输入的气缸未确认机械到位。");
    return firstError;
}

short CGtMotionController::MovePoint(short axis, long targetPos,
                                     double targetVel, double acc, double dec,
                                     volatile LONG* stopRequested)
{
    if (!stopRequested || targetVel <= 0 || targetVel > kMaxSpeedPulsePerMs ||
        acc <= 0 || dec <= 0) return -103;
    if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;

    long sts = 0;
    double startPos = 0.0;
    double prfPos = 0.0;
    TTrapPrm trap = {};
    short rc = GT_GetPrfPos(axis, &startPos);
    LogResult(L"GT_GetPrfPos", rc);
    if (rc != 0)
        return rc;

    // 当前规划位置已经接近目标，无需启动运动。
    if (fabs(startPos - (double)targetPos) <= kPositionTolerance)
    {
        Log(L"规划位置已接近目标位置，无需移动。");
        return 0;
    }

    // 根据目标位置与当前规划位置确定运动方向。
    const int direction = (targetPos > startPos) ? 1 : -1;

    // 允许从单侧限位向外退离，但禁止继续驶向该侧限位。
    // 两侧限位同时触发时，CheckCanMove() 会拒绝运动。
    rc = CheckCanMove(axis, direction, true);
    if (rc != 0)
    {
        switch (rc)
        {
        case -112:
            Log(L"运动被限位保护阻止：存在限位状态。");
            break;
        case -113:
            Log(L"运动被限位保护阻止：正负限位同时触发。");
            break;
        case -114:
            Log(L"运动被限位保护阻止：目标方向继续驶向正限位。");
            break;
        case -115:
            Log(L"运动被限位保护阻止：目标方向继续驶向负限位。");
            break;
        default:
            Log(L"运动被安全检查阻止，请检查伺服、报警和急停状态。");
            break;
        }
        return rc;
    }

    rc = GT_PrfTrap(axis); LogResult(L"GT_PrfTrap", rc); if (rc != 0) return rc;
    rc = GT_GetTrapPrm(axis, &trap); LogResult(L"GT_GetTrapPrm", rc); if (rc != 0) return rc;
    trap.acc = acc;
    trap.dec = dec;
    rc = GT_SetTrapPrm(axis, &trap); LogResult(L"GT_SetTrapPrm", rc); if (rc != 0) return rc;
    rc = GT_SetPos(axis, targetPos); LogResult(L"GT_SetPos", rc); if (rc != 0) return rc;
    rc = GT_SetVel(axis, targetVel); LogResult(L"GT_SetVel", rc); if (rc != 0) return rc;
    if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;

    const long mask = AxisMask(axis);
    rc = GT_Update(mask); LogResult(L"GT_Update", rc); if (rc != 0) return rc;
    Log(L"点位运动已下发。");

    DWORD begin = GetTickCount();
    DWORD lastPublish = begin;
    DWORD lastDiag = begin;
    bool started = false;
    while (GetTickCount() - begin < kPointTimeoutMs)
    {
        rc = CheckSafety(stopRequested);
        if (rc != 0)
        {
            StopAndWait(mask, kStopWaitTimeoutMs);
            return rc;
        }
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0)
        {
            short stopRc = StopAndWait(mask, kStopWaitTimeoutMs);
            return stopRc == 0 ? -105 : stopRc;
        }
        rc = GT_GetSts(axis, &sts);
        if (rc != 0) { StopAndWait(mask, kStopWaitTimeoutMs); LogResult(L"GT_GetSts", rc); return rc; }
        rc = GT_GetPrfPos(axis, &prfPos);
        if (rc != 0) { StopAndWait(mask, kStopWaitTimeoutMs); LogResult(L"GT_GetPrfPos", rc); return rc; }
        if (sts & STS_MOVING) started = true;

        if (GetTickCount() - lastDiag >= 500)
        {
            wchar_t diag[320] = {};

            _snwprintf_s(
                diag,
                _countof(diag),
                _TRUNCATE,
                L"轴%d诊断：STS=0x%08lX，伺服状态位=%d，"
                L"规划运动位=%d，规划位置=%.1f；设备为开环步进，无编码器反馈",
                (int)axis,
                (unsigned long)sts,
                (int)((sts & STS_SERVO_ON) != 0),
                (int)((sts & STS_MOVING) != 0),
                prfPos
            );

            Log(diag);
            lastDiag = GetTickCount();
        }

        if (GetTickCount() - lastPublish >= 200)
        {
            PublishAxisStatus();
            lastPublish = GetTickCount();
        }

        if (!(sts & STS_MOVING) && fabs(prfPos - (double)targetPos) <= kPositionTolerance)
        {
            wchar_t result[256] = {};

            _snwprintf_s(
                result,
                _countof(result),
                _TRUNCATE,
                L"规划位置已到目标：目标=%.1f，规划位置=%.1f；机械位置没有编码器反馈确认",
                (double)targetPos,
                prfPos
            );

            Log(result);
            Log(L"开环步进模式：本次任务按规划器完成判定，实际机械位置需由操作员确认。");
            return 0;
        }
        if (!started && GetTickCount() - begin > kStartTimeoutMs)
        {
            StopAndWait(mask, kStopWaitTimeoutMs);
            Log(L"未检测到运动启动；未将停止状态误判为成功。");
            return -106;
        }
        if (started && !(sts & STS_MOVING))
        {
            StopAndWait(mask, kStopWaitTimeoutMs);
            Log(L"轴提前停止，规划位置未达到目标。");
            return -107;
        }
        Sleep(10);
    }
    StopAndWait(mask, kStopWaitTimeoutMs);
    Log(L"点位运动超时，已请求停止。");
    return -104;
}

short CGtMotionController::MoveSequence(const long targetPos[4],
                                         const double targetVel[4],
                                         double acc, double dec,
                                         volatile LONG* stopRequested)
{
    if (!targetPos || !targetVel) return -103;
    for (short axis = 1; axis <= 3; ++axis)
    {
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;
        wchar_t log[100] = {};
        _snwprintf_s(log, _countof(log), _TRUNCATE, L"准备启动 %d 轴。", axis);
        Log(log);
        wchar_t progress[100] = {};
        _snwprintf_s(progress, _countof(progress), _TRUNCATE,
                     L"步骤 %d/3：运行 %d 轴点位运动", axis, axis);
        Progress(axis, 3, progress);
        short rc = MovePoint(axis, targetPos[axis], targetVel[axis], acc, dec, stopRequested);
        if (rc != 0)
        {
            Log(L"当前轴运动未成功完成，后续轴已取消启动。");
            return rc;
        }
    }
    Log(L"1→2→3 轴依次运动完成。");
    return 0;
}

short CGtMotionController::HomeSequence(const AxisHomeSettings settings[4],
                                         bool resetOutputs,
                                         const bool extendLevelHigh[4],
                                         const bool resetExtend[4],
                                         bool polarityConfirmed,
                                         volatile LONG* stopRequested)
{
    if (!settings || !stopRequested) return -103;
    if (resetOutputs && (!polarityConfirmed || !extendLevelHigh || !resetExtend)) return -131;
    if (resetOutputs && !m_extensionReady) return -130;

    const short order[] = { 3, 1, 2 };
    for (size_t i = 0; i < _countof(order); ++i)
    {
        const short axis = order[i];
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0)
            return -105;

        wchar_t log[100] = {};
        _snwprintf_s(log, _countof(log), _TRUNCATE, L"准备对 %d 轴执行回零。", axis);
        Log(log);
        wchar_t progress[100] = {};
        _snwprintf_s(progress, _countof(progress), _TRUNCATE,
                     L"步骤 %d/3：对 %d 轴执行 HOME", (int)i + 1, axis);
        Progress((int)i + 1, 3, progress);

        short rc = HomeAxis(axis, settings[axis], stopRequested);
        if (rc != 0)
        {
            Log(L"当前轴回零未成功完成，后续轴已取消回零。");
            return rc;
        }
    }

    Log(L"3→1→2 轴依次回零完成。");
    if (resetOutputs)
    {
        if (CheckSafety(stopRequested) != 0) return -116;
        return ResetMachineOutputs(extendLevelHigh, resetExtend, polarityConfirmed);
    }
    return 0;
}

short CGtMotionController::JogHold(short axis, int direction, double speed,
                                   double acc, double dec,
                                   volatile LONG* stopRequested)
{
    if (!stopRequested || (direction != -1 && direction != 1) ||
        speed <= 0 || speed > kMaxSpeedPulsePerMs || acc <= 0 || dec <= 0)
        return -103;
    if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return 0;

    short rc = CheckCanMove(axis, direction, true);
    if (rc != 0)
    {
        Log(L"JOG 被安全检查阻止：请检查报警、急停和限位方向。");
        return rc;
    }

    rc = GT_PrfJog(axis); LogResult(L"GT_PrfJog", rc); if (rc != 0) return rc;
    TJogPrm jog;
    rc = GT_GetJogPrm(axis, &jog); LogResult(L"GT_GetJogPrm", rc); if (rc != 0) return rc;
    jog.acc = acc;
    jog.dec = dec;
    jog.smooth = 0;
    rc = GT_SetJogPrm(axis, &jog); LogResult(L"GT_SetJogPrm", rc); if (rc != 0) return rc;
    if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return 0;

    rc = GT_SetVel(axis, direction > 0 ? speed : -speed);
    LogResult(L"GT_SetVel(JOG)", rc); if (rc != 0) return rc;
    const long mask = AxisMask(axis);
    rc = GT_Update(mask); LogResult(L"GT_Update(JOG)", rc); if (rc != 0) return rc;

    Log(direction > 0 ? L"正向 JOG 已启动，松开按钮停止。" : L"负向 JOG 已启动，松开按钮停止。");
    DWORD begin = GetTickCount(), lastPublish = begin;
    while (InterlockedCompareExchange(stopRequested, 0, 0) == 0)
    {
        rc = CheckSafety(stopRequested);
        if (rc != 0) break;
        if (GetTickCount() - begin >= kJogWatchdogMs)
        {
            Log(L"JOG 达到软件看门狗上限，自动请求停止。");
            break;
        }
        long sts = 0;
        rc = GT_GetSts(axis, &sts);
        if (rc != 0) { StopAndWait(mask, kStopWaitTimeoutMs); LogResult(L"GT_GetSts(JOG)", rc); return rc; }
        if (sts & STS_DRIVE_ALARM) { Log(L"JOG 检测到驱动报警，停止本次点动。"); break; }
        if (sts & STS_ESTOP_IO) { Log(L"JOG 检测到急停输入，停止本次点动。"); break; }
        if ((direction > 0 && (sts & STS_POS_LIMIT)) ||
            (direction < 0 && (sts & STS_NEG_LIMIT)))
        { Log(L"JOG 已到达运动方向上的限位，停止本次点动。"); break; }
        if (GetTickCount() - lastPublish >= 200)
        {
            PublishAxisStatus();
            lastPublish = GetTickCount();
        }
        Sleep(10);
    }
    rc = StopAndWait(mask, kStopWaitTimeoutMs);
    Log(rc == 0 ? L"JOG 已停止。" : L"JOG 停止状态未确认，请检查设备。");
    return rc;
}

short CGtMotionController::HomeAxis(short axis, const AxisHomeSettings& settings,
                                    volatile LONG* stopRequested)
{
    const int direction = settings.direction;
    const double highVel = settings.highVel;
    const double lowVel = settings.lowVel;
    const double acc = settings.acc;
    const double dec = settings.dec;
    const long searchDistance = settings.searchDistance;
    if (!stopRequested || axis < 1 || axis > 3 ||
        (direction != -1 && direction != 1) || highVel <= 0 || lowVel <= 0 ||
        lowVel > highVel || highVel > kMaxSpeedPulsePerMs ||
        acc <= 0 || dec <= 0 || searchDistance <= 0)
        return -103;
    if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;

    short safetyRc = CheckSafety(stopRequested);
    if (safetyRc != 0) return safetyRc;

    // This example uses Smart Home mode 20 (HOME input only). It assumes the
    // HOME input is correctly wired/configured in GTS800.cfg and its search
    // direction/signal edge are known. Use the local GTS manual for exact mode.
    short rc = CheckCanMove(axis, direction, true);
    if (rc != 0)
    {
        Log(L"回零被安全检查阻止。若限位已触发，请先用安全方式退离限位并确认两端状态正常。");
        return rc;
    }

    THomePrm home = {};
    rc = GT_GetHomePrm(axis, &home);
    LogResult(L"GT_GetHomePrm", rc);
    if (rc != 0) return rc;
    if (settings.confirmationRequired &&
        (home.triggerIndex != settings.confirmedTriggerIndex ||
         home.edge != settings.confirmedEdge ||
         home.moveDir != settings.confirmedControllerDirection))
    {
        wchar_t changed[180] = {};
        _snwprintf_s(changed, _countof(changed), _TRUNCATE,
                     L"%d 轴 HOME 配置在现场确认后发生变化：触发器=%d/%d，触发沿=%d/%d，控制器方向=%d/%d；本次回零已阻止，请重新读取并确认。",
                     axis, home.triggerIndex, settings.confirmedTriggerIndex,
                     home.edge, settings.confirmedEdge, home.moveDir,
                     settings.confirmedControllerDirection);
        Log(changed);
        return -122;
    }

    home.mode = 20;                 // HOME-switch only; requires real HOME signal
    home.moveDir = (short)direction;
    home.velHigh = highVel;
    home.velLow = lowVel;
    home.acc = acc;
    home.dec = dec;
    home.homeOffset = 0;
    home.searchHomeDistance = searchDistance;
    // Keep the configured triggerIndex (the GTS default is the current axis),
    // capture edge, and other fields returned by GT_GetHomePrm.
    if (settings.overrideTriggerIndex) home.triggerIndex = settings.triggerIndex;
    if (settings.overrideEdge) home.edge = settings.edge;
    wchar_t configText[180] = {};
    _snwprintf_s(configText, _countof(configText), _TRUNCATE,
                 L"%d 轴 HOME 参数：模式=%d，触发器=%d，捕获沿=%d，搜索方向=%d，高速=%.3f，低速=%.3f，距离=%ld。",
                 axis, home.mode, home.triggerIndex, home.edge, home.moveDir,
                 home.velHigh, home.velLow, home.searchHomeDistance);
    Log(configText);

    m_axisHomed[axis] = false;
    rc = GT_GoHome(axis, &home);
    LogResult(L"GT_GoHome", rc);
    if (rc != 0) return rc;

    Progress(1, 1, L"所选轴 HOME 搜索运行中");
    Log(L"回零已启动，等待 HOME 信号和回零状态。请勿操作其他运动控件。");
    DWORD begin = GetTickCount(), lastPublish = begin;
    bool sawRunning = false;

    while (GetTickCount() - begin < kHomeTimeoutMs)
    {
        rc = CheckSafety(stopRequested);
        if (rc != 0)
        {
            StopAndWait(AxisMask(axis), kStopWaitTimeoutMs);
            return rc;
        }
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0)
        {
            short stopRc = StopAndWait(AxisMask(axis), kStopWaitTimeoutMs);
            Log(L"回零收到软件停止请求。");
            return stopRc == 0 ? -105 : stopRc;
        }

        THomeStatus hs = {};
        rc = GT_GetHomeStatus(axis, &hs);
        if (rc != 0)
        {
            StopAndWait(AxisMask(axis), kStopWaitTimeoutMs);
            LogResult(L"GT_GetHomeStatus", rc);
            return rc;
        }
        if (hs.run != 0) sawRunning = true;

        long sts = 0;
        rc = GT_GetSts(axis, &sts);
        if (rc != 0)
        {
            StopAndWait(AxisMask(axis), kStopWaitTimeoutMs);
            LogResult(L"GT_GetSts(HOME)", rc);
            return rc;
        }
        short limitRc = 0;
        if (sts & STS_DRIVE_ALARM) limitRc = -110;
        else if (sts & STS_ESTOP_IO) limitRc = -111;
        else if ((direction > 0 && (sts & STS_POS_LIMIT))) limitRc = -114;
        else if ((direction < 0 && (sts & STS_NEG_LIMIT))) limitRc = -115;
        if (limitRc != 0)
        {
            StopAndWait(AxisMask(axis), kStopWaitTimeoutMs);
            wchar_t blocked[160] = {};
            _snwprintf_s(blocked, _countof(blocked), _TRUNCATE,
                         L"%d 轴 HOME 搜索被状态/限位阻止：状态=0x%08lX，HOME阶段=%d，捕获位置=%ld；后续轴已取消。",
                         axis, sts, hs.stage, hs.capturePos);
            Log(blocked);
            PublishHomeDiagnostics();
            return limitRc;
        }

        if (GetTickCount() - lastPublish >= 200)
        {
            PublishAxisStatus();
            PublishHomeDiagnostics();
            lastPublish = GetTickCount();
        }

        if (sawRunning && hs.run == 0)
        {
            if (hs.error != 0)
            {
                wchar_t err[128] = {};
                _snwprintf_s(err, _countof(err), _TRUNCATE,
                             L"%d 轴回零结束但控制器报告错误：%d，阶段：%d，捕获位置：%ld，目标位置：%ld。",
                             axis, hs.error, hs.stage, hs.capturePos, hs.targetPos);
                Log(err);
                if (hs.error == HOME_ERROR_NO_HOME &&
                    hs.stage == HOME_STAGE_SEARCH_HOME)
                {
                    Log(L"HOME 搜索阶段未捕获到原点信号。请核对该轴 HOME 输入接线/映射、"
                        L"输入有效电平、搜索方向及搜索距离；未确认 HOME 前不会启动下一轴。");
                }
                PublishHomeDiagnostics();
                return (short)(hs.error == 0 ? -120 : hs.error);
            }
            rc = GT_ZeroPos(axis);
            LogResult(L"GT_ZeroPos(回零完成)", rc);
            if (rc != 0) return rc;
            m_axisHomed[axis] = true;
            PublishHomeDiagnostics();
            Progress(1, 1, L"所选轴 HOME 完成，指令坐标已置零");
            Log(L"回零完成，当前位置已设置为坐标零点。");
            return 0;
        }

        if (!sawRunning && GetTickCount() - begin > kStartTimeoutMs)
        {
            StopAndWait(AxisMask(axis), kStopWaitTimeoutMs);
            Log(L"未检测到回零进入运行状态。检查 HOME 输入、方向和模式配置。");
            return -121;
        }
        Sleep(10);
    }

    StopAndWait(AxisMask(axis), kStopWaitTimeoutMs);
    Log(L"回零超时，已请求停止。请检查 HOME 输入、方向和搜索距离。");
    return -104;
}

void CGtMotionController::PublishAxisStatus() const
{
    if (!m_initialized || !m_notifyHwnd) return;
    GtsAxisStatusPacket* packet = new (std::nothrow) GtsAxisStatusPacket;
    if (!packet) return;
    ZeroMemory(packet, sizeof(*packet));
    packet->opened = m_opened;
    packet->initialized = m_initialized;
    packet->extensionReady = m_extensionReady;
    for (short axis = 1; axis <= 3; ++axis)
    {
        packet->axisEnabled[axis - 1] = m_axisEnabled[axis];
        GtsAxisStatusRow& row = packet->rows[axis - 1];
        row.statusRc = GT_GetSts(axis, &row.status);
        row.prfRc = GT_GetPrfPos(axis, &row.prfPos);
    }
    if (!::PostMessageW(m_notifyHwnd, WM_GTS_AXIS_STATUS, 0,
                        reinterpret_cast<LPARAM>(packet)))
        delete packet;
}

void CGtMotionController::Progress(int step, int total, const wchar_t* text) const
{
    if (!m_notifyHwnd || !text) return;
    GtsProgressPacket* packet = new (std::nothrow) GtsProgressPacket;
    if (!packet) return;
    packet->step = step;
    packet->total = total;
    wcsncpy_s(packet->text, _countof(packet->text), text, _TRUNCATE);
    if (!::PostMessageW(m_notifyHwnd, WM_GTS_PROGRESS, 0,
                        reinterpret_cast<LPARAM>(packet)))
        delete packet;
}

short CGtMotionController::ClearAlarms()
{
    long inputs = 0;
    short rc = ReadDigitalInputs(inputs);
    if (rc != 0) return rc;
    const bool lightActive = (((inputs >> 4) & 1) != 0) == m_lightCurtainActiveHigh;
    const bool stopActive = (((inputs >> 1) & 1) != 0) == m_stopInputActiveHigh;
    if (lightActive || stopActive)
    {
        Log(L"安全输入仍处于触发状态，未清除联锁。请先恢复现场并确认输入极性。");
        return -116;
    }
    rc = GT_ClrSts(1, 3);
    LogResult(L"GT_ClrSts(1, 3)", rc);
    if (rc != 0) return rc;
    m_safetyTripped = false;
    m_safetySource = GTS_SAFETY_NONE;
    SetDirectOutput(0, false);
    SetDirectOutput(3, false);
    Log(L"报警/联锁复位完成。确认机械状态后再重新使能伺服。");
    return 0;
}

short CGtMotionController::ZeroAxis(short axis)
{
    if (axis < 1 || axis > 3 || !m_initialized) return -103;
    long sts = 0;
    short rc = GT_GetSts(axis, &sts);
    if (rc != 0) return rc;
    if (sts & STS_MOVING) return -132;
    rc = GT_ZeroPos(axis);
    LogResult(L"GT_ZeroPos(手动位置清零)", rc);
    if (rc == 0)
    {
        m_axisHomed[axis] = false;
        Log(L"指令坐标已清零；这不会替代 HOME 回零，也不会证明机械轴位于物理原点。");
    }
    return rc;
}

short CGtMotionController::CapturePlannedPositions(long positions[4])
{
    if (!positions || !m_initialized) return -103;
    positions[0] = 0;
    for (short axis = 1; axis <= 3; ++axis)
    {
        double value = 0.0;
        short rc = GT_GetPrfPos(axis, &value);
        if (rc != 0) return rc;
        positions[axis] = (long)value;
    }
    return 0;
}

short CGtMotionController::PollIoStatus()
{
    if (!m_initialized || !m_notifyHwnd) return 0;
    GtsIoStatusPacket* packet = new (std::nothrow) GtsIoStatusPacket;
    if (!packet) return -103;
    ZeroMemory(packet, sizeof(*packet));
    packet->extensionReady = m_extensionReady;
    packet->directInputRc = GT_GetDi(MC_GPI, &packet->directInputs);
    packet->directOutputRc = GT_GetDo(MC_GPO, &packet->directOutputs);
    if (m_extensionReady)
    {
        packet->extensionInputRc = GT_GetExtIoValue(0, &packet->extensionInputs);
        packet->extensionOutputRc = GT_GetExtDoValue(0, &packet->extensionOutputs);
    }
    else
    {
        packet->extensionInputRc = -130;
        packet->extensionOutputRc = -130;
    }
    if (packet->directInputRc == 0)
    {
        packet->lightCurtainRaw = ((packet->directInputs >> 4) & 1) != 0;
        packet->stopInputRaw = ((packet->directInputs >> 1) & 1) != 0;
        packet->lightCurtainActive = packet->lightCurtainRaw == m_lightCurtainActiveHigh;
        packet->stopInputActive = packet->stopInputRaw == m_stopInputActiveHigh;
    }
    packet->safetyActive = packet->lightCurtainActive || packet->stopInputActive || m_safetyTripped;
    if (packet->directInputRc == 0 && (packet->lightCurtainActive || packet->stopInputActive))
        CheckSafety(NULL);
    packet->safetySource = (packet->lightCurtainActive ? GTS_SAFETY_LIGHT_CURTAIN : GTS_SAFETY_NONE) |
                          (packet->stopInputActive ? GTS_SAFETY_SYSTEM_STOP : GTS_SAFETY_NONE);
    if (packet->safetySource == GTS_SAFETY_NONE && m_safetyTripped)
        packet->safetySource = m_safetySource;
    const short result = packet->directInputRc;
    if (!::PostMessageW(m_notifyHwnd, WM_GTS_IO_STATUS, 0,
                        reinterpret_cast<LPARAM>(packet)))
        delete packet;
    return result;
}

short CGtMotionController::PublishHomeDiagnostics() const
{
    if (!m_initialized || !m_notifyHwnd) return -101;
    GtsHomeDiagnosticsPacket* packet = new (std::nothrow) GtsHomeDiagnosticsPacket;
    if (!packet) return -103;
    ZeroMemory(packet, sizeof(*packet));
    packet->inputRc = GT_GetDi(MC_GPI, &packet->directInputs);
    short result = packet->inputRc;
    for (short axis = 1; axis <= 3; ++axis)
    {
        GtsHomeDiagnosticRow& row = packet->rows[axis - 1];
        row.axis = axis;
        THomePrm prm = {};
        row.homePrmRc = GT_GetHomePrm(axis, &prm);
        if (row.homePrmRc == 0)
        {
            row.triggerIndex = prm.triggerIndex;
            row.edge = prm.edge;
            row.moveDir = prm.moveDir;
        }
        else if (result == 0) result = row.homePrmRc;
        row.statusRc = GT_GetSts(axis, &row.status);
        if (row.statusRc != 0 && result == 0) result = row.statusRc;
        THomeStatus homeStatus = {};
        row.homeStatusRc = GT_GetHomeStatus(axis, &homeStatus);
        if (row.homeStatusRc == 0)
        {
            row.run = homeStatus.run;
            row.stage = homeStatus.stage;
            row.error = homeStatus.error;
            row.capturePos = homeStatus.capturePos;
            row.targetPos = homeStatus.targetPos;
        }
        else if (result == 0) result = row.homeStatusRc;
    }
    if (!::PostMessageW(m_notifyHwnd, WM_GTS_HOME_DIAGNOSTICS, 0,
                        reinterpret_cast<LPARAM>(packet)))
        delete packet;
    return result;
}

short CGtMotionController::WaitForCoordinate(volatile LONG* stopRequested,
                                             DWORD timeoutMs)
{
    DWORD begin = GetTickCount();
    DWORD lastPublish = begin;
    bool sawRunning = false;
    for (;;)
    {
        short rc = CheckSafety(stopRequested);
        if (rc != 0)
        {
            StopAndWait(0x7, kStopWaitTimeoutMs);
            GT_CrdClear(1, 0);
            return rc;
        }
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0)
        {
            StopAndWait(0x7, kStopWaitTimeoutMs);
            GT_CrdClear(1, 0);
            return -105;
        }
        short run = 0;
        long segment = 0;
        rc = GT_CrdStatus(1, &run, &segment, 0);
        if (rc != 0)
        {
            StopAndWait(0x7, kStopWaitTimeoutMs);
            GT_CrdClear(1, 0);
            LogResult(L"GT_CrdStatus", rc);
            return rc;
        }
        if (run) sawRunning = true;
        // Some GTS firmware reports idle for the first polling cycle after CrdStart.
        // Require either a running observation or a short minimum settle window.
        if (!run && (sawRunning || GetTickCount() - begin >= 100)) return 0;
        if (GetTickCount() - begin >= timeoutMs)
        {
            StopAndWait(0x7, kStopWaitTimeoutMs);
            GT_CrdClear(1, 0);
            Log(L"坐标系插补超时，已请求停止并清空缓冲区。");
            return -104;
        }
        if (GetTickCount() - lastPublish >= 200)
        {
            PublishAxisStatus();
            lastPublish = GetTickCount();
        }
        Sleep(10);
    }
}

short CGtMotionController::MoveCoordinated(const long target[4], double velocity,
                                            double acceleration,
                                            volatile LONG* stopRequested)
{
    if (!target || !stopRequested || velocity <= 0 || acceleration <= 0)
        return -103;
    for (short axis = 1; axis <= 3; ++axis)
    {
        if (!m_axisEnabled[axis]) return -102;
        if (m_axisHomed[axis] == false)
        {
            Log(L"三轴联动前必须完成三轴 HOME 回零。");
            return -133;
        }
    }
    short rc = CheckSafety(stopRequested);
    if (rc != 0) return rc;

    TCrdPrm prm = {};
    prm.dimension = 3;
    // TCrdPrm.profile is indexed by physical planner axis and stores the
    // coordinate dimension (1=X, 2=Y, 3=Z), so invert the UI's XYZ->axis map.
    for (short axis = 1; axis <= 3; ++axis) prm.profile[axis - 1] = 0;
    for (short coordinate = 0; coordinate < 3; ++coordinate)
        prm.profile[m_axisForXyz[coordinate] - 1] = (short)(coordinate + 1);
    prm.synVelMax = velocity;
    prm.synAccMax = acceleration;
    prm.evenTime = 0;
    prm.setOriginFlag = 0;
    rc = GT_SetCrdPrm(1, &prm);
    LogResult(L"GT_SetCrdPrm(1)", rc);
    if (rc != 0) return rc;
    rc = GT_CrdClear(1, 0);
    LogResult(L"GT_CrdClear(1)", rc);
    if (rc != 0) return rc;
    rc = GT_LnXYZ(1, target[m_axisForXyz[0]], target[m_axisForXyz[1]],
                  target[m_axisForXyz[2]], velocity,
                  acceleration, 0, 0);
    LogResult(L"GT_LnXYZ", rc);
    if (rc != 0) return rc;
    rc = GT_CrdStart(0x1, 0);
    LogResult(L"GT_CrdStart(1)", rc);
    if (rc != 0) return rc;
    rc = WaitForCoordinate(stopRequested, kPointTimeoutMs);
    if (rc != 0) return rc;

    for (short axis = 1; axis <= 3; ++axis)
    {
        double actualCommand = 0.0;
        rc = GT_GetPrfPos(axis, &actualCommand);
        if (rc != 0) return rc;
        if (fabs(actualCommand - (double)target[axis]) > kPositionTolerance)
        {
            Log(L"坐标系状态结束，但规划位置未到目标；未启动后续流程步骤。");
            return -107;
        }
    }
    Log(L"三轴坐标系规划到位；开环设备无法确认机械轴实际位置。");
    return 0;
}

short CGtMotionController::RunTrajectory(const GtsTrajectoryRequest& request,
                                          volatile LONG* stopRequested)
{
    if (!stopRequested || request.velocity <= 0 || request.acceleration <= 0)
        return -103;
    long current[4] = {};
    short rc = CapturePlannedPositions(current);
    if (rc != 0) return rc;
    for (short axis = 1; axis <= 3; ++axis)
    {
        if (!m_axisEnabled[axis] || !m_axisHomed[axis])
        {
            Log(L"轨迹插补需要三轴伺服已使能且完成 HOME 回零。");
            return -133;
        }
    }
    rc = CheckSafety(stopRequested);
    if (rc != 0) return rc;

    TCrdPrm prm = {};
    prm.dimension = 3;
    for (short axis = 1; axis <= 3; ++axis) prm.profile[axis - 1] = 0;
    for (short coordinate = 0; coordinate < 3; ++coordinate)
        prm.profile[m_axisForXyz[coordinate] - 1] = (short)(coordinate + 1);
    prm.synVelMax = request.velocity;
    prm.synAccMax = request.acceleration;
    prm.setOriginFlag = 0;
    rc = GT_SetCrdPrm(1, &prm); LogResult(L"GT_SetCrdPrm(轨迹)", rc); if (rc != 0) return rc;
    rc = GT_CrdClear(1, 0); LogResult(L"GT_CrdClear(轨迹)", rc); if (rc != 0) return rc;

    const long z = request.kind == GTS_TRAJ_LINE ? request.z : current[m_axisForXyz[2]];
    if (request.kind == GTS_TRAJ_LINE)
    {
        rc = GT_LnXYZ(1, request.x, request.y, request.z,
                      request.velocity, request.acceleration, 0, 0);
        LogResult(L"GT_LnXYZ(直线)", rc);
    }
    else if (request.kind == GTS_TRAJ_ARC)
    {
        // GT_ArcXYC takes the center as an offset from the segment start.
        const long centerOffsetX = request.centerX - current[m_axisForXyz[0]];
        const long centerOffsetY = request.centerY - current[m_axisForXyz[1]];
        rc = GT_ArcXYC(1, request.x, request.y, centerOffsetX,
                       centerOffsetY, 0, request.velocity,
                       request.acceleration, 0, 0);
        LogResult(L"GT_ArcXYC(圆弧)", rc);
    }
    else if (request.kind == GTS_TRAJ_TRIANGLE)
    {
        if (request.radius <= 0) return -103;
        const double root3 = 1.7320508075688772;
        const long x1 = request.centerX + request.radius;
        const long y1 = request.centerY;
        const long x2 = request.centerX - request.radius / 2;
        const long y2 = request.centerY + (long)(request.radius * root3 / 2.0);
        const long x3 = request.centerX - request.radius / 2;
        const long y3 = request.centerY - (long)(request.radius * root3 / 2.0);
        rc = GT_LnXYZ(1, x1, y1, z, request.velocity, request.acceleration, 0, 0);
        if (rc == 0) rc = GT_LnXYZ(1, x2, y2, z, request.velocity, request.acceleration, 0, 0);
        if (rc == 0) rc = GT_LnXYZ(1, x3, y3, z, request.velocity, request.acceleration, 0, 0);
        if (rc == 0) rc = GT_LnXYZ(1, x1, y1, z, request.velocity, request.acceleration, 0, 0);
        LogResult(L"GT_LnXYZ(正三角形)", rc);
    }
    else if (request.kind == GTS_TRAJ_CIRCLE)
    {
        if (request.radius <= 0) return -103;
        const long cx = request.centerX, cy = request.centerY, r = request.radius;
        rc = GT_LnXYZ(1, cx + r, cy, z, request.velocity, request.acceleration, 0, 0);
        if (rc == 0) rc = GT_ArcXYC(1, cx, cy + r, -r, 0, 0, request.velocity, request.acceleration, 0, 0);
        if (rc == 0) rc = GT_ArcXYC(1, cx - r, cy, 0, -r, 0, request.velocity, request.acceleration, 0, 0);
        if (rc == 0) rc = GT_ArcXYC(1, cx, cy - r, r, 0, 0, request.velocity, request.acceleration, 0, 0);
        if (rc == 0) rc = GT_ArcXYC(1, cx + r, cy, 0, r, 0, request.velocity, request.acceleration, 0, 0);
        LogResult(L"GT_ArcXYC(圆形轨迹)", rc);
    }
    else return -103;
    if (rc != 0) return rc;
    Progress(1, 2, L"步骤 1/2：坐标系轨迹启动并运行");
    rc = GT_CrdStart(0x1, 0); LogResult(L"GT_CrdStart(轨迹)", rc); if (rc != 0) return rc;
    rc = WaitForCoordinate(stopRequested, kPointTimeoutMs);
    if (rc != 0) return rc;

    long expected[4] = {};
    for (short axis = 1; axis <= 3; ++axis) expected[axis] = current[axis];
    long endX = request.x;
    long endY = request.y;
    long endZ = request.kind == GTS_TRAJ_LINE ? request.z : current[m_axisForXyz[2]];
    if (request.kind == GTS_TRAJ_TRIANGLE || request.kind == GTS_TRAJ_CIRCLE)
    {
        endX = request.centerX + request.radius;
        endY = request.centerY;
    }
    expected[m_axisForXyz[0]] = endX;
    expected[m_axisForXyz[1]] = endY;
    expected[m_axisForXyz[2]] = endZ;
    for (short axis = 1; axis <= 3; ++axis)
    {
        double planned = 0.0;
        rc = GT_GetPrfPos(axis, &planned);
        LogResult(L"GT_GetPrfPos(轨迹终点核对)", rc);
        if (rc != 0) return rc;
        if (fabs(planned - (double)expected[axis]) > kPositionTolerance)
        {
            Log(L"插补状态已结束，但规划位置未到预期终点；未报告轨迹完成。");
            return -107;
        }
    }
    Progress(2, 2, L"步骤 2/2：规划终点已核对");
    Log(L"轨迹规划终点已核对；开环设备无法确认机械轨迹实际精度。");
    return rc;
}

short CGtMotionController::RunPickPlace(const GtsPickPlaceRecipe& recipe,
                                        DWORD cylinderDwellMs,
                                        DWORD rodlessTimeoutMs,
                                        const bool extendLevelHigh[4],
                                        const bool resetExtend[4],
                                        bool polarityConfirmed,
                                        bool rodlessInPositionActiveHigh,
                                        bool rodlessHomeActiveHigh,
                                        volatile LONG* stopRequested)
{
    if (!stopRequested || !extendLevelHigh || !resetExtend || !polarityConfirmed ||
        !m_extensionReady || rodlessTimeoutMs == 0)
        return !m_extensionReady ? -130 : -131;
    for (short axis = 1; axis <= 3; ++axis)
    {
        if (!m_axisHomed[axis] || !m_axisEnabled[axis])
        {
            Log(L"自动抓放要求三轴已使能并完成 HOME 回零。");
            return -133;
        }
    }

    short rc = CheckSafety(stopRequested);
    if (rc != 0) return rc;
    Progress(1, 9, L"步骤 1/9：打开绿灯，准备启动抓放周期");
    rc = SetLogicalOutput(GTS_OUT_GREEN, true, extendLevelHigh); if (rc != 0) return rc;

    Progress(2, 9, L"步骤 2/9：无杆气缸伸出，等待 DI0 到位");
    rc = SetLogicalOutput(GTS_OUT_RODLESS, true, extendLevelHigh); if (rc != 0) return rc;
    DWORD begin = GetTickCount();
    for (;;)
    {
        rc = CheckSafety(stopRequested); if (rc != 0) return rc;
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;
        unsigned short extInputs = 0;
        rc = GT_GetExtIoValue(0, &extInputs);
        if (rc != 0) { LogResult(L"GT_GetExtIoValue(等待无杆到位)", rc); return rc; }
        if (((extInputs & 0x0001) != 0) == rodlessInPositionActiveHigh) break; // gLink DI0
        if (GetTickCount() - begin >= rodlessTimeoutMs)
        {
            Log(L"等待 gLink DI0 无杆气缸到位超时；后续抓放步骤已取消。");
            return -134;
        }
        Sleep(20);
    }

    Progress(3, 9, L"步骤 3/9：二层气缸推出；等待设定延时（无独立行程反馈）");
    rc = SetLogicalOutput(GTS_OUT_BIN2, true, extendLevelHigh); if (rc != 0) return rc;
    begin = GetTickCount();
    while (GetTickCount() - begin < cylinderDwellMs)
    {
        rc = CheckSafety(stopRequested); if (rc != 0) return rc;
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;
        Sleep(10);
    }

    Progress(4, 9, L"步骤 4/9：三轴插补移动至示教抓取位，夹爪夹紧并打开真空");
    rc = MoveCoordinated(recipe.pick, recipe.velocity[1], recipe.acceleration, stopRequested);
    if (rc != 0) return rc;
    rc = SetLogicalOutput(GTS_OUT_GRIPPER, true, extendLevelHigh); if (rc != 0) return rc;
    rc = SetLogicalOutput(GTS_OUT_VACUUM, true, extendLevelHigh); if (rc != 0) return rc;
    begin = GetTickCount();
    while (GetTickCount() - begin < cylinderDwellMs)
    {
        rc = CheckSafety(stopRequested); if (rc != 0) return rc;
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;
        Sleep(10);
    }

    Progress(5, 9, L"步骤 5/9：三轴插补移动至二层 1 号放置位，释放夹爪和真空");
    rc = MoveCoordinated(recipe.place, recipe.velocity[1], recipe.acceleration, stopRequested);
    if (rc != 0) return rc;
    rc = SetLogicalOutput(GTS_OUT_VACUUM, false, extendLevelHigh); if (rc != 0) return rc;
    rc = SetLogicalOutput(GTS_OUT_GRIPPER, false, extendLevelHigh); if (rc != 0) return rc;

    Progress(6, 9, L"步骤 6/9：二层气缸收回");
    rc = SetLogicalOutput(GTS_OUT_BIN2, resetExtend[2], extendLevelHigh); if (rc != 0) return rc;
    begin = GetTickCount();
    while (GetTickCount() - begin < cylinderDwellMs)
    {
        rc = CheckSafety(stopRequested); if (rc != 0) return rc;
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;
        Sleep(10);
    }

    Progress(7, 9, L"步骤 7/9：无杆气缸按配置复位，等待 DI0/DI1 对应端位");
    rc = SetLogicalOutput(GTS_OUT_RODLESS, resetExtend[1], extendLevelHigh); if (rc != 0) return rc;
    begin = GetTickCount();
    for (;;)
    {
        rc = CheckSafety(stopRequested); if (rc != 0) return rc;
        if (InterlockedCompareExchange(stopRequested, 0, 0) != 0) return -105;
        unsigned short extInputs = 0;
        rc = GT_GetExtIoValue(0, &extInputs);
        if (rc != 0) { LogResult(L"GT_GetExtIoValue(等待无杆复位到位)", rc); return rc; }
        const unsigned short targetMask = resetExtend[1] ? 0x0001 : 0x0002;
        const bool activeHigh = resetExtend[1]
            ? rodlessInPositionActiveHigh : rodlessHomeActiveHigh;
        if (((extInputs & targetMask) != 0) == activeHigh) break;
        if (GetTickCount() - begin >= rodlessTimeoutMs)
        {
            Log(resetExtend[1]
                ? L"等待 gLink DI0 无杆气缸伸出到位超时；后续步骤已取消。"
                : L"等待 gLink DI1 无杆气缸回原位超时；后续步骤已取消。");
            return -134;
        }
        Sleep(20);
    }

    Progress(8, 9, L"步骤 8/9：三轴插补返回示教安全零位");
    rc = MoveCoordinated(recipe.safe, recipe.velocity[1], recipe.acceleration, stopRequested);
    if (rc != 0) return rc;
    Progress(9, 9, L"步骤 9/9：关闭绿灯，抓放周期完成");
    rc = SetLogicalOutput(GTS_OUT_GREEN, false, extendLevelHigh);
    if (rc == 0) Log(L"抓放单次周期完成。指令位置来自规划器，机械位置无编码器反馈确认。");
    return rc;
}

short CGtMotionController::Close()
{
    if (!m_opened) return 0;
    short firstError = DisableAxes();
    if (m_extensionReady)
    {
        short extRc = GT_CloseExtMdl();
        LogResult(L"GT_CloseExtMdl", extRc);
        if (extRc != 0 && firstError == 0) firstError = extRc;
        m_extensionReady = false;
    }
    short rc = GT_Close();
    LogResult(L"GT_Close", rc);
    if (rc != 0 && firstError == 0) firstError = rc;
    m_opened = false;
    m_initialized = false;
    m_safetyTripped = false;
    for (int i = 1; i <= 3; ++i) m_axisHomed[i] = false;
    return firstError;
}
