#pragma once
#include <Windows.h>
#include "MotionMessages.h"
#include "gts.h"

struct AxisHomeSettings
{
    int direction;
    double highVel;
    double lowVel;
    double acc;
    double dec;
    long searchDistance;
    bool overrideTriggerIndex;
    short triggerIndex;
    bool overrideEdge;
    short edge;
    bool confirmationRequired;
    short confirmedTriggerIndex;
    short confirmedEdge;
    short confirmedControllerDirection;
};

enum GtsLogicalOutput
{
    GTS_OUT_RED = 0,
    GTS_OUT_YELLOW,
    GTS_OUT_GREEN,
    GTS_OUT_BUZZER,
    GTS_OUT_SCREWDRIVER,
    GTS_OUT_GRIPPER,
    GTS_OUT_VACUUM,
    GTS_OUT_PRESS_CYLINDER,
    GTS_OUT_RODLESS,
    GTS_OUT_BIN2,
    GTS_OUT_BIN3
};

enum GtsTrajectoryKind
{
    GTS_TRAJ_LINE = 1,
    GTS_TRAJ_ARC,
    GTS_TRAJ_TRIANGLE,
    GTS_TRAJ_CIRCLE
};

struct GtsTrajectoryRequest
{
    int kind;
    long x;
    long y;
    long z;
    long centerX;
    long centerY;
    long radius;
    double velocity;
    double acceleration;
};

struct GtsPickPlaceRecipe
{
    long pick[4];
    long place[4];
    long safe[4];
    double velocity[4];
    double acceleration;
};

class CGtMotionController
{
public:
    CGtMotionController();

    short Initialize(HWND notifyHwnd, bool lightCurtainActiveHigh = true,
                     bool stopInputActiveHigh = true);
    short EnableAxes();
    short DisableAxes();
    short ClearAlarms();
    short ZeroAxis(short axis);
    short SetLogicalOutput(int output, bool on,
                           const bool extendLevelHigh[4] = NULL);
    short ResetMachineOutputs(const bool extendLevelHigh[4],
                              const bool resetExtend[4],
                              bool polarityConfirmed);
    short MovePoint(short axis, long targetPos, double targetVel,
                    double acc, double dec, volatile LONG* stopRequested);
    short MoveSequence(const long targetPos[4], const double targetVel[4],
                       double acc, double dec, volatile LONG* stopRequested);
    short HomeAxis(short axis, const AxisHomeSettings& settings,
                   volatile LONG* stopRequested);
    short HomeSequence(const AxisHomeSettings settings[4], bool resetOutputs,
                       const bool extendLevelHigh[4], const bool resetExtend[4],
                       bool polarityConfirmed,
                       volatile LONG* stopRequested);
    short JogHold(short axis, int direction, double speed, double acc, double dec,
                  volatile LONG* stopRequested);
    short RunTrajectory(const GtsTrajectoryRequest& request,
                        volatile LONG* stopRequested);
    short RunPickPlace(const GtsPickPlaceRecipe& recipe, DWORD cylinderDwellMs,
                       DWORD rodlessTimeoutMs, const bool extendLevelHigh[4],
                       const bool resetExtend[4], bool polarityConfirmed,
                       bool rodlessInPositionActiveHigh,
                       bool rodlessHomeActiveHigh,
                       volatile LONG* stopRequested);
    short CapturePlannedPositions(long positions[4]);
    short PollIoStatus();
    short PublishHomeDiagnostics() const;
    short Close();

    bool IsInitialized() const { return m_initialized; }
    bool IsOpened() const { return m_opened; }
    bool IsExtensionReady() const { return m_extensionReady; }
    bool IsAxisHomed(short axis) const;
    void SetNotifyWindow(HWND notifyHwnd) { m_notifyHwnd = notifyHwnd; }
    bool SetCoordinateMapping(const short axisForXyz[3]);
    void SetSafetyInputPolarity(bool lightCurtainActiveHigh,
                                bool stopInputActiveHigh);
    short ApplySafetyInputPolarity(bool lightCurtainActiveHigh,
                                   bool stopInputActiveHigh);
    void PublishAxisStatus() const;
    void Log(const wchar_t* text) const;
    void Progress(int step, int total, const wchar_t* text) const;

private:
    bool m_opened;
    bool m_initialized;
    bool m_extensionReady;
    bool m_axisEnabled[4];
    bool m_axisHomed[4];
    short m_axisForXyz[3];
    bool m_safetyTripped;
    int m_safetySource;
    bool m_lightCurtainActiveHigh;
    bool m_stopInputActiveHigh;
    HWND m_notifyHwnd;

    void LogResult(const wchar_t* functionName, short result) const;
    short CheckCanMove(short axis, int direction, bool allowRetreatFromLimit) const;
    short StopAndWait(long mask, DWORD timeoutMs);
    short CheckSafety(volatile LONG* stopRequested);
    short ReadDigitalInputs(long& inputs) const;
    short SetDirectOutput(short index, bool value);
    short SetExtensionOutput(short index, bool value);
    short MoveCoordinated(const long target[4], double velocity, double acceleration,
                          volatile LONG* stopRequested);
    short WaitForCoordinate(volatile LONG* stopRequested, DWORD timeoutMs);
};
