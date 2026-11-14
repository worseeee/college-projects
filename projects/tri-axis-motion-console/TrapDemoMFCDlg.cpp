#include "pch.h"
#include "TrapDemoMFCDlg.h"
#include <tchar.h>
#include <stdlib.h>
#include <float.h>
#include <math.h>
#include <vector>

namespace
{
    const int kPageOverview = 0;
    const int kPageManual = 1;
    const int kPageIo = 2;
    const int kPageAuto = 3;
    const int kPageTrajectory = 4;
    const int kPageSettings = 5;
    const int kBaseWidth = 1240;
    const int kBaseHeight = 850;
    const int kPageOriginX = 24;
    const int kPageOriginY = 93;
    const int kAxisOrder[3] = { 3, 1, 2 };
    const int kOutputCount = 11;
    const wchar_t* kOutputNames[kOutputCount] = {
        L"红色指示灯", L"黄色指示灯", L"绿色指示灯", L"蜂鸣器",
        L"电批启动", L"夹爪夹紧", L"真空吸附", L"压缸伸出",
        L"无杆气缸伸出", L"二层气缸推出", L"三层气缸推出"
    };
    const int kDirectInputBits[] = { 0, 1, 2, 3, 4, 7, 8, 9 };
    const wchar_t* kDirectInputNames[] = {
        L"系统启动 EXI0", L"系统停止 EXI1", L"系统复位 EXI2",
        L"电批急停 EXI3", L"光幕 EXI4", L"电批完成 EXI7",
        L"压缸上位 EXI8", L"压缸下位 EXI9"
    };
    const int kExtensionInputBits[] = { 0, 1, 4, 5, 6, 9, 10, 11, 12, 13, 14 };
    const wchar_t* kExtensionInputNames[] = {
        L"无杆气缸到位 DI0", L"无杆气缸原位 DI1",
        L"三层 1 号位 DI4", L"三层 2 号位 DI5", L"三层 3 号位 DI6",
        L"二层 1 号位 DI9", L"二层 2 号位 DI10", L"二层 3 号位 DI11",
        L"一层 1 号位 DI12", L"一层 2 号位 DI13", L"一层 3 号位 DI14"
    };

    bool SameHomeSettings(const AxisHomeSettings& a, const AxisHomeSettings& b)
    {
        return a.direction == b.direction &&
               fabs(a.highVel - b.highVel) < 1e-9 &&
               fabs(a.lowVel - b.lowVel) < 1e-9 &&
               fabs(a.acc - b.acc) < 1e-9 &&
               fabs(a.dec - b.dec) < 1e-9 &&
               a.searchDistance == b.searchDistance &&
               a.overrideTriggerIndex == b.overrideTriggerIndex &&
               (!a.overrideTriggerIndex || a.triggerIndex == b.triggerIndex) &&
               a.overrideEdge == b.overrideEdge &&
               (!a.overrideEdge || a.edge == b.edge);
    }

    CString NumberText(long value)
    {
        CString text;
        text.Format(_T("%ld"), value);
        return text;
    }

    UINT DpiForWindow(HWND hwnd)
    {
        HMODULE user32 = ::GetModuleHandleW(L"user32.dll");
        typedef UINT (WINAPI* GetDpiForWindowProc)(HWND);
        GetDpiForWindowProc getDpi = user32
            ? reinterpret_cast<GetDpiForWindowProc>(::GetProcAddress(user32, "GetDpiForWindow"))
            : NULL;
        const UINT dpi = getDpi ? getDpi(hwnd) : 96;
        return dpi == 0 ? 96 : dpi;
    }
}

BEGIN_MESSAGE_MAP(CPageViewport, CWnd)
    ON_WM_HSCROLL()
    ON_WM_VSCROLL()
    ON_MESSAGE(WM_GTS_JOG_BUTTON_DOWN, &CPageViewport::OnJogButtonDown)
    ON_MESSAGE(WM_GTS_JOG_BUTTON_UP, &CPageViewport::OnJogButtonUp)
END_MESSAGE_MAP()

CPageViewport::CPageViewport()
    : m_contentWidth(0), m_contentHeight(0), m_scrollX(0), m_scrollY(0), m_scale(1.0)
{
}

BOOL CPageViewport::Create(CWnd* parent, UINT id)
{
    LPCTSTR className = AfxRegisterWndClass(CS_HREDRAW | CS_VREDRAW,
        ::LoadCursor(NULL, IDC_ARROW), (HBRUSH)(COLOR_WINDOW + 1), NULL);
    return CreateEx(WS_EX_CONTROLPARENT, className, _T(""),
        WS_CHILD | WS_HSCROLL | WS_VSCROLL | WS_CLIPCHILDREN,
        CRect(0, 0, 0, 0), parent, id);
}

BOOL CPageViewport::OnCommand(WPARAM wParam, LPARAM lParam)
{
    CWnd* parent = GetParent();
    return parent ? (BOOL)parent->SendMessage(WM_COMMAND, wParam, lParam) : FALSE;
}

BOOL CPageViewport::OnNotify(WPARAM wParam, LPARAM lParam, LRESULT* pResult)
{
    CWnd* parent = GetParent();
    if (!parent) return FALSE;
    if (pResult) *pResult = parent->SendMessage(WM_NOTIFY, wParam, lParam);
    return TRUE;
}

LRESULT CPageViewport::OnJogButtonDown(WPARAM wParam, LPARAM lParam)
{
    CWnd* parent = GetParent();
    return parent ? parent->SendMessage(WM_GTS_JOG_BUTTON_DOWN, wParam, lParam) : 0;
}

LRESULT CPageViewport::OnJogButtonUp(WPARAM wParam, LPARAM lParam)
{
    CWnd* parent = GetParent();
    return parent ? parent->SendMessage(WM_GTS_JOG_BUTTON_UP, wParam, lParam) : 0;
}

void CPageViewport::RegisterControl(HWND hwnd, const RECT& logicalRect)
{
    if (!::IsWindow(hwnd)) return;
    ChildLayout child = {};
    child.hwnd = hwnd;
    child.rect = logicalRect;
    m_children.push_back(child);
    LayoutChildren();
}

void CPageViewport::SetLayoutScale(double scale)
{
    m_scale = scale > 0.0 ? scale : 1.0;
    LayoutChildren();
}

void CPageViewport::LayoutChildren()
{
    for (size_t i = 0; i < m_children.size(); ++i)
    {
        const ChildLayout& child = m_children[i];
        if (!::IsWindow(child.hwnd)) continue;
        const int left = (int)(child.rect.left * m_scale + 0.5) - m_scrollX;
        const int top = (int)(child.rect.top * m_scale + 0.5) - m_scrollY;
        const int width = max(1, (int)((child.rect.right - child.rect.left) * m_scale + 0.5));
        const int height = max(1, (int)((child.rect.bottom - child.rect.top) * m_scale + 0.5));
        ::MoveWindow(child.hwnd, left, top, width, height, TRUE);
    }
}

void CPageViewport::SetContentSize(int width, int height)
{
    m_contentWidth = max(0, width);
    m_contentHeight = max(0, height);
    CRect client;
    GetClientRect(&client);
    SCROLLINFO si = {};
    si.cbSize = sizeof(si);
    si.fMask = SIF_RANGE | SIF_PAGE | SIF_POS;
    si.nMin = 0;
    si.nMax = max(0, m_contentWidth - 1);
    si.nPage = max(1, client.Width());
    si.nPos = m_scrollX;
    SetScrollInfo(SB_HORZ, &si, TRUE);
    si.nMax = max(0, m_contentHeight - 1);
    si.nPage = max(1, client.Height());
    si.nPos = m_scrollY;
    SetScrollInfo(SB_VERT, &si, TRUE);
    ScrollTo(m_scrollX, m_scrollY);
}

void CPageViewport::ResetScroll()
{
    ScrollTo(0, 0);
    SetScrollPos(SB_HORZ, 0, TRUE);
    SetScrollPos(SB_VERT, 0, TRUE);
}

void CPageViewport::ScrollTo(int x, int y)
{
    CRect client;
    GetClientRect(&client);
    x = max(0, min(x, max(0, m_contentWidth - client.Width())));
    y = max(0, min(y, max(0, m_contentHeight - client.Height())));
    if (m_scrollX == x && m_scrollY == y) return;
    m_scrollX = x;
    m_scrollY = y;
    SetScrollPos(SB_HORZ, m_scrollX, TRUE);
    SetScrollPos(SB_VERT, m_scrollY, TRUE);
    LayoutChildren();
    Invalidate(FALSE);
}

void CPageViewport::OnHScroll(UINT code, UINT, CScrollBar*)
{
    CRect client;
    GetClientRect(&client);
    SCROLLINFO si = {};
    si.cbSize = sizeof(si);
    si.fMask = SIF_TRACKPOS;
    GetScrollInfo(SB_HORZ, &si);
    int pos = m_scrollX;
    switch (code)
    {
    case SB_LINELEFT: pos -= 28; break;
    case SB_LINERIGHT: pos += 28; break;
    case SB_PAGELEFT: pos -= max(28, client.Width() - 28); break;
    case SB_PAGERIGHT: pos += max(28, client.Width() - 28); break;
    case SB_THUMBPOSITION:
    case SB_THUMBTRACK: pos = si.nTrackPos; break;
    default: return;
    }
    ScrollTo(pos, m_scrollY);
}

void CPageViewport::OnVScroll(UINT code, UINT, CScrollBar*)
{
    CRect client;
    GetClientRect(&client);
    SCROLLINFO si = {};
    si.cbSize = sizeof(si);
    si.fMask = SIF_TRACKPOS;
    GetScrollInfo(SB_VERT, &si);
    int pos = m_scrollY;
    switch (code)
    {
    case SB_LINEUP: pos -= 24; break;
    case SB_LINEDOWN: pos += 24; break;
    case SB_PAGEUP: pos -= max(24, client.Height() - 24); break;
    case SB_PAGEDOWN: pos += max(24, client.Height() - 24); break;
    case SB_THUMBPOSITION:
    case SB_THUMBTRACK: pos = si.nTrackPos; break;
    default: return;
    }
    ScrollTo(m_scrollX, pos);
}

BEGIN_MESSAGE_MAP(CTrapDemoMFCDlg, CDialogEx)
    ON_MESSAGE(WM_GTS_MOTION_LOG, &CTrapDemoMFCDlg::OnMotionLog)
    ON_MESSAGE(WM_GTS_MOTION_DONE, &CTrapDemoMFCDlg::OnMotionDone)
    ON_MESSAGE(WM_GTS_JOG_BUTTON_DOWN, &CTrapDemoMFCDlg::OnJogButtonDown)
    ON_MESSAGE(WM_GTS_JOG_BUTTON_UP, &CTrapDemoMFCDlg::OnJogButtonUp)
    ON_MESSAGE(WM_GTS_AXIS_STATUS, &CTrapDemoMFCDlg::OnAxisStatus)
    ON_MESSAGE(WM_GTS_IO_STATUS, &CTrapDemoMFCDlg::OnIoStatus)
    ON_MESSAGE(WM_GTS_PROGRESS, &CTrapDemoMFCDlg::OnProgress)
    ON_MESSAGE(WM_GTS_CAPTURE_POS, &CTrapDemoMFCDlg::OnCapturePosition)
    ON_MESSAGE(WM_GTS_HOME_DIAGNOSTICS, &CTrapDemoMFCDlg::OnHomeDiagnostics)
    ON_NOTIFY(TCN_SELCHANGE, IDC_TAB_MAIN, &CTrapDemoMFCDlg::OnTabChanged)
    ON_WM_SIZE()
    ON_WM_GETMINMAXINFO()
    ON_WM_DESTROY()
END_MESSAGE_MAP()

CTrapDemoMFCDlg::CTrapDemoMFCDlg(CWnd* pParent)
    : CDialogEx(IDD_TRAPDEMOMFC_DIALOG, pParent),
      m_pWorker(NULL), m_commandEvent(FALSE, FALSE), m_busy(0),
      m_stopRequested(0), m_shutdown(0), m_activeCommand(GTS_CMD_NONE),
      m_activeJogDirection(0), m_demoCurtain(0), m_demoStop(0), m_lastCommandAxis(1), m_uiInitialized(false),
      m_uiServoEnabled(false), m_extensionReady(false), m_closing(false),
      m_demoMode(false), m_safetyTripped(false), m_safetyInputsValid(false),
      m_safetySource(GTS_SAFETY_NONE), m_polarityConfirmed(false),
      m_lightCurtainActiveHigh(true), m_stopInputActiveHigh(true),
      m_pendingLightCurtainActiveHigh(true), m_pendingStopInputActiveHigh(true),
      m_rodlessInPositionActiveHigh(true), m_rodlessHomeActiveHigh(true),
      m_cylinderDwellMs(800), m_rodlessTimeoutMs(10000), m_activePage(kPageOverview),
      m_simInitialized(false), m_simInputs(0), m_simOutputs(0),
      m_simExtInputs(0x0001), m_simExtOutputs(0), m_progressLabelId(IDC_STATIC_PROGRESS),
      m_controllerStatusId(IDC_STATIC_CTRL_STATUS), m_hardwareStatusId(IDC_STATIC_HW_STATUS),
      m_extensionStatusId(IDC_STATIC_EXTENSION), m_feedbackStatusId(IDC_STATIC_FEEDBACK)
{
    ZeroMemory(&m_request, sizeof(m_request));
    ZeroMemory(m_taughtPositions, sizeof(m_taughtPositions));
    ZeroMemory(m_simPosition, sizeof(m_simPosition));
    for (int i = 0; i < 4; ++i)
    {
        m_axisHomed[i] = false;
        m_homeConfirmed[i] = false;
        m_homeDiagnosticsReceived[i] = false;
        m_homeTriggerIndex[i] = -1;
        m_homeTriggerEdge[i] = -1;
        m_homeControllerDirection[i] = 0;
        m_simEnabled[i] = false;
        m_simHomed[i] = false;
        m_taught[i] = false;
        m_extendLevelHigh[i] = true;
        m_resetExtend[i] = false;
        m_homeSettings[i].direction = -1;
        m_homeSettings[i].highVel = 2.0;
        m_homeSettings[i].lowVel = 0.5;
        m_homeSettings[i].acc = 0.1;
        m_homeSettings[i].dec = 0.1;
        m_homeSettings[i].searchDistance = 200000;
        m_homeSettings[i].overrideTriggerIndex = false;
        m_homeSettings[i].triggerIndex = -1;
        m_homeSettings[i].overrideEdge = false;
        m_homeSettings[i].edge = 0;
        m_homeSettings[i].confirmationRequired = false;
        m_homeSettings[i].confirmedTriggerIndex = -1;
        m_homeSettings[i].confirmedEdge = -1;
        m_homeSettings[i].confirmedControllerDirection = 0;
        ZeroMemory(&m_homeConfirmedSettings[i], sizeof(m_homeConfirmedSettings[i]));
    }
    m_homeRawInputs = 0;
    m_homeInputReadRc = -1;
    m_homeSettings[1].direction = -1;
    m_homeSettings[2].direction = -1;
    m_homeSettings[3].direction = -1;
    m_axisForXyz[0] = 1; m_axisForXyz[1] = 2; m_axisForXyz[2] = 3;
    m_request.command = GTS_CMD_NONE;
}

void CTrapDemoMFCDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialogEx::DoDataExchange(pDX);
}

HWND CTrapDemoMFCDlg::AddControl(int page, int id, LPCWSTR className,
                                  LPCWSTR text, DWORD style, int x, int y,
                                  int width, int height, DWORD exStyle)
{
    const DWORD windowStyle = WS_CHILD | style;
    HWND parent = page < 0 ? m_hWnd : m_pageViewports[page].GetSafeHwnd();
    const int left = page < 0 ? x : x - kPageOriginX;
    const int top = page < 0 ? y : y - kPageOriginY;
    HWND hwnd = ::CreateWindowExW(exStyle, className, text, windowStyle,
                                  left, top, width, height, parent,
                                  reinterpret_cast<HMENU>(static_cast<INT_PTR>(id)),
                                  AfxGetInstanceHandle(), NULL);
    if (!hwnd) return NULL;
    if (m_uiFont.GetSafeHandle())
        ::SendMessageW(hwnd, WM_SETFONT, (WPARAM)(HFONT)m_uiFont.GetSafeHandle(), TRUE);
    LayoutEntry entry = {};
    entry.hwnd = hwnd;
    entry.rect.left = left; entry.rect.top = top;
    entry.rect.right = left + width; entry.rect.bottom = top + height;
    entry.page = page;
    m_layoutEntries.push_back(entry);
    if (page >= 0) m_pageViewports[page].RegisterControl(hwnd, entry.rect);
    ::ShowWindow(hwnd, page < 0 || page == m_activePage ? SW_SHOW : SW_HIDE);
    return hwnd;
}

HWND CTrapDemoMFCDlg::AddLabel(int page, int id, LPCWSTR text, int x, int y,
                                int width, int height)
{
    return AddControl(page, id, L"STATIC", text,
                      SS_LEFT | SS_CENTERIMAGE, x, y, width, height);
}

HWND CTrapDemoMFCDlg::AddButton(int page, int id, LPCWSTR text, int x, int y,
                                 int width, int height, DWORD style)
{
    return AddControl(page, id, L"BUTTON", text,
                      style | WS_TABSTOP, x, y, width, height);
}

HWND CTrapDemoMFCDlg::AddEdit(int page, int id, LPCWSTR value, int x, int y,
                               int width, int height, DWORD extraStyle)
{
    return AddControl(page, id, L"EDIT", value,
                      WS_BORDER | ES_AUTOHSCROLL | WS_TABSTOP | extraStyle,
                      x, y, width, height, WS_EX_CLIENTEDGE);
}

HWND CTrapDemoMFCDlg::AddCheck(int page, int id, LPCWSTR text, int x, int y,
                                int width, int height, bool checked)
{
    HWND hwnd = AddControl(page, id, L"BUTTON", text,
                           BS_AUTOCHECKBOX | WS_TABSTOP, x, y, width, height);
    if (hwnd) ::SendMessageW(hwnd, BM_SETCHECK, checked ? BST_CHECKED : BST_UNCHECKED, 0);
    return hwnd;
}

HWND CTrapDemoMFCDlg::AddGroup(int page, int id, LPCWSTR text, int x, int y,
                                int width, int height)
{
    return AddControl(page, id, L"BUTTON", text, BS_GROUPBOX, x, y, width, height);
}

void CTrapDemoMFCDlg::AddIoRow(int row, int output, LPCWSTR name, int page,
                                int x, int y, bool)
{
    AddLabel(page, IDC_IO_STATUS_BASE + output, name, x, y, 190, 28);
    AddButton(page, IDC_IO_ON_BASE + output, L"动作", x + 198, y, 72, 28);
    AddButton(page, IDC_IO_OFF_BASE + output, L"复位", x + 278, y, 72, 28);
    const int stateId = IDC_IO_STATUS_BASE + 20 + output;
    AddLabel(page, stateId, L"状态：--", x + 360, y, 130, 28);
    m_outputStatusIds.push_back(stateId);
    (void)row;
}

BOOL CTrapDemoMFCDlg::OnInitDialog()
{
    CDialogEx::OnInitDialog();

    // Resource-editor controls from the starter dialog are replaced by the tabbed runtime UI.
    for (HWND child = ::GetWindow(m_hWnd, GW_CHILD); child; )
    {
        HWND next = ::GetWindow(child, GW_HWNDNEXT);
        ::DestroyWindow(child);
        child = next;
    }

    RECT work = {};
    SystemParametersInfo(SPI_GETWORKAREA, 0, &work, 0);
    const int width = max(640, min(kBaseWidth, (int)(work.right - work.left - 24)));
    const int height = max(500, min(kBaseHeight, (int)(work.bottom - work.top - 40)));
    SetWindowPos(NULL, 0, 0, width, height,
                 SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE);
    CenterWindow();
    SetWindowText(_T("固高三轴运动控制台 | GTS-800-PG"));

    // The vendor controller loads GTS800.cfg and ExtMdl.cfg by relative path.
    wchar_t modulePath[MAX_PATH] = {};
    if (::GetModuleFileNameW(NULL, modulePath, _countof(modulePath)) != 0)
    {
        wchar_t* slash = wcsrchr(modulePath, L'\\');
        if (slash) { *slash = L'\0'; ::SetCurrentDirectoryW(modulePath); }
    }

    const int fontHeight = max(14, ::MulDiv(16, (int)DpiForWindow(m_hWnd), 96));
    m_uiFont.CreateFontW(fontHeight, 0, 0, 0, FW_NORMAL, FALSE, FALSE, 0,
                         DEFAULT_CHARSET, OUT_DEFAULT_PRECIS,
                         CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
                         DEFAULT_PITCH | FF_DONTCARE, L"Microsoft YaHei UI");
    m_backgroundBrush.CreateSolidBrush(RGB(246, 248, 251));
    m_motion.SetNotifyWindow(m_hWnd);
    LoadSettings();
    CreateUi();
    ApplyPageVisibility(m_activePage);

    m_pWorker = AfxBeginThread(&CTrapDemoMFCDlg::WorkerThreadProc, this,
                               THREAD_PRIORITY_NORMAL, 0, CREATE_SUSPENDED);
    if (m_pWorker == NULL)
    {
        AfxMessageBox(_T("创建运动工作线程失败。"));
        return TRUE;
    }
    m_pWorker->m_bAutoDelete = FALSE;
    m_pWorker->ResumeThread();
    AppendLogUi(L"控制台启动。硬件模式默认开启；无反馈步进设备只显示规划位置，不显示虚假的编码器位置。");
    AppendLogUi(L"请先核实 HOME、限位、光幕与急停接线，再初始化、使能和运动。软件联锁不替代硬件安全回路。");
    UpdateUiState();
    return TRUE;
}

void CTrapDemoMFCDlg::CreateUi()
{
    HWND tabHwnd = AddControl(-1, IDC_TAB_MAIN, WC_TABCONTROLW, L"",
                              WS_VISIBLE | WS_TABSTOP | TCS_TABS,
                              14, 52, 1212, 698);
    m_tab.SubclassWindow(tabHwnd);
    for (int i = 0; i < 6; ++i) m_pageViewports[i].Create(this, 3490 + i);
    const wchar_t* tabs[] = { L"总览", L"手动轴控", L"IO 控制", L"自动抓放", L"轨迹插补", L"设置诊断" };
    for (int i = 0; i < 6; ++i)
    {
        TCITEMW item = {};
        item.mask = TCIF_TEXT;
        item.pszText = const_cast<LPWSTR>(tabs[i]);
        m_tab.InsertItem(i, &item);
    }
    m_tab.SetCurSel(m_activePage);

    AddLabel(-1, m_controllerStatusId, L"控制器：未初始化", 22, 12, 250, 25);
    AddLabel(-1, m_extensionStatusId, L"gLink200：未连接", 278, 12, 220, 25);
    AddLabel(-1, m_feedbackStatusId, L"位置反馈：开环，无编码器", 505, 12, 235, 25);
    AddLabel(-1, m_hardwareStatusId, L"安全状态：等待初始化", 750, 12, 245, 25);
    AddLabel(-1, 3090, L"模式", 1000, 12, 38, 24);
    HWND mode = AddControl(-1, IDC_COMBO_MODE, L"COMBOBOX", L"",
                           CBS_DROPDOWNLIST | WS_VSCROLL | WS_TABSTOP,
                           1040, 11, 122, 240);
    ::SendMessageW(mode, CB_ADDSTRING, 0, (LPARAM)L"硬件控制");
    ::SendMessageW(mode, CB_ADDSTRING, 0, (LPARAM)L"隔离演示");
    ::SendMessageW(mode, CB_SETCURSEL, m_demoMode ? 1 : 0, 0);
    AddButton(-1, IDC_BTN_INIT, L"初始化", 22, 39, 90, 28);
    AddButton(-1, IDC_BTN_ENABLE, L"伺服使能", 120, 39, 90, 28);
    AddButton(-1, IDC_BTN_DISABLE, L"伺服关闭", 218, 39, 90, 28);
    AddButton(-1, IDC_BTN_STOP, L"停止当前任务", 316, 39, 118, 28);
    AddCheck(-1, IDC_CHECK_OPERATOR_SAFE, L"我已确认现场安全条件", 447, 39, 190, 28, false);
    AddLabel(-1, m_progressLabelId, L"当前任务：空闲", 652, 39, 548, 28);

    // Persistent footer log.
    AddLabel(-1, 3091, L"运行日志", 22, 757, 90, 20);
    HWND logHwnd = AddControl(-1, IDC_EDIT_LOG_NEW, L"EDIT", L"",
                              ES_MULTILINE | ES_READONLY | ES_AUTOVSCROLL |
                              WS_VSCROLL | WS_TABSTOP,
                              22, 780, 1080, 55, WS_EX_CLIENTEDGE);
    m_logEdit.SubclassWindow(logHwnd);
    AddCheck(-1, IDC_CHECK_LOG_AUTOSCROLL, L"自动滚动", 1110, 780, 105, 26, true);
    AddButton(-1, IDC_BTN_CLEAR_LOG, L"清空日志", 1110, 810, 105, 26);

    // Overview page.
    AddGroup(kPageOverview, 3092, L"三轴实时状态 | 规划位置单位：pulse", 24, 93, 810, 270);
    HWND listHwnd = AddControl(kPageOverview, IDC_LIST_AXIS_STATUS, WC_LISTVIEWW, L"",
                               LVS_REPORT | LVS_SHOWSELALWAYS | WS_BORDER | WS_TABSTOP,
                               36, 119, 786, 228, WS_EX_CLIENTEDGE);
    m_axisStatusList.SubclassWindow(listHwnd);
    InitAxisStatusList();
    AddGroup(kPageOverview, 3093, L"控制器与硬件诊断", 850, 93, 355, 270);
    AddLabel(kPageOverview, 3094, L"状态位：伺服、运动、限位、报警", 870, 122, 315, 26);
    AddLabel(kPageOverview, 3095, L"位置来源：规划器指令位置", 870, 157, 315, 26);
    AddLabel(kPageOverview, 3096, L"本设备无编码器反馈；机械实际位置未被软件确认。", 870, 192, 315, 52);
    AddLabel(kPageOverview, 3097, L"光幕/系统停止输入触发时软件请求停轴并锁止新动作。", 870, 252, 315, 52);
    AddLabel(kPageOverview, 3098, L"软件逻辑不能替代硬件安全继电器和急停回路。", 870, 313, 315, 35);
    AddGroup(kPageOverview, 3099, L"常用操作", 24, 377, 1181, 285);
    AddButton(kPageOverview, IDC_BTN_HOME_SEQUENCE, L"三轴依次回零  (3 → 1 → 2)", 45, 414, 250, 42);
    AddButton(kPageOverview, IDC_BTN_HOME_RESET, L"回零并复位气缸/灯", 310, 414, 230, 42);
    AddButton(kPageOverview, IDC_BTN_START_AUTO, L"启动一次抓放周期", 555, 414, 220, 42);
    AddButton(kPageOverview, IDC_BTN_IO_REFRESH, L"刷新 IO 状态", 790, 414, 170, 42);
    AddLabel(kPageOverview, 3100, L"请在“手动轴控”页配置每轴回零方向；在“设置诊断”页确认气缸输出极性后才能执行气缸复位。", 45, 482, 1110, 48);
    AddLabel(kPageOverview, 3101, L"教学演示模式完全隔离 GTS API；切换到硬件模式后，所有运动和 IO 命令仍通过后台工作线程串行执行。", 45, 546, 1110, 48);

    // Manual page.
    AddGroup(kPageManual, 3102, L"轴选择与点位参数", 24, 94, 1180, 195);
    AddLabel(kPageManual, 3103, L"当前轴", 43, 124, 70, 27);
    HWND axisCombo = AddControl(kPageManual, IDC_COMBO_AXIS_NEW, L"COMBOBOX", L"",
                                CBS_DROPDOWNLIST | WS_VSCROLL | WS_TABSTOP,
                                111, 123, 100, 200);
    ::SendMessageW(axisCombo, CB_ADDSTRING, 0, (LPARAM)L"1 轴");
    ::SendMessageW(axisCombo, CB_ADDSTRING, 0, (LPARAM)L"2 轴");
    ::SendMessageW(axisCombo, CB_ADDSTRING, 0, (LPARAM)L"3 轴");
    ::SendMessageW(axisCombo, CB_SETCURSEL, 0, 0);
    const int posIds[] = { IDC_EDIT_POS1_NEW, IDC_EDIT_POS2_NEW, IDC_EDIT_POS3_NEW };
    const int velIds[] = { IDC_EDIT_VEL1_NEW, IDC_EDIT_VEL2_NEW, IDC_EDIT_VEL3_NEW };
    for (int i = 0; i < 3; ++i)
    {
        CString label;
        label.Format(_T("%d 轴目标位置"), i + 1);
        AddLabel(kPageManual, 3110 + i, label, 250 + i * 210, 120, 118, 24);
        AddEdit(kPageManual, posIds[i], L"", 370 + i * 210, 120, 95, 28);
        label.Format(_T("%d 轴速度"), i + 1);
        AddLabel(kPageManual, 3120 + i, label, 250 + i * 210, 158, 118, 24);
        AddEdit(kPageManual, velIds[i], L"1.0", 370 + i * 210, 158, 95, 28);
    }
    AddLabel(kPageManual, 3130, L"加速度", 880, 120, 90, 24);
    AddEdit(kPageManual, IDC_EDIT_ACC_NEW, L"0.25", 970, 120, 100, 28);
    AddLabel(kPageManual, 3131, L"减速度", 880, 158, 90, 24);
    AddEdit(kPageManual, IDC_EDIT_DEC_NEW, L"0.25", 970, 158, 100, 28);
    AddButton(kPageManual, IDC_BTN_MOVE, L"所选轴点位运动", 43, 214, 200, 44);
    AddButton(kPageManual, IDC_BTN_SEQUENCE, L"一键三轴依次运动", 260, 214, 220, 44);

    AddGroup(kPageManual, 3132, L"按住点动 | 松开即停", 24, 306, 370, 135);
    AddLabel(kPageManual, 3133, L"JOG 速度", 45, 340, 92, 26);
    AddEdit(kPageManual, IDC_EDIT_JOG_SPEED_NEW, L"0.1", 137, 338, 90, 28);
    AddLabel(kPageManual, 3134, L"加速度", 45, 378, 92, 26);
    AddEdit(kPageManual, IDC_EDIT_JOG_ACC_NEW, L"0.1", 137, 376, 90, 28);
    AddLabel(kPageManual, 3135, L"减速度", 245, 340, 70, 26);
    AddEdit(kPageManual, IDC_EDIT_JOG_DEC_NEW, L"0.1", 310, 338, 65, 28);
    HWND negJog = AddButton(kPageManual, IDC_BTN_JOG_NEG, L"负向 JOG", 45, 409, 145, 25);
    HWND posJog = AddButton(kPageManual, IDC_BTN_JOG_POS, L"正向 JOG", 205, 409, 160, 25);
    m_btnJogNegative.SubclassWindow(negJog);
    m_btnJogPositive.SubclassWindow(posJog);
    m_btnJogNegative.SetDirection(-1);
    m_btnJogPositive.SetDirection(1);

    AddGroup(kPageManual, 3136, L"逐轴 HOME 参数", 414, 306, 790, 280);
    const wchar_t* homeHead[] = { L"轴", L"方向", L"高速", L"低速", L"加速", L"减速", L"搜索距离", L"当前触发器 / 沿 / 限位" };
    const int homeXs[] = { 430, 468, 527, 590, 653, 716, 779, 864 };
    const int homeWidths[] = { 34, 55, 58, 58, 58, 58, 80, 215 };
    for (int c = 0; c < 8; ++c) AddLabel(kPageManual, 3140 + c, homeHead[c], homeXs[c], 338, homeWidths[c], 24);
    const int dirIds[] = { IDC_EDIT_HOME_DIR1, IDC_EDIT_HOME_DIR2, IDC_EDIT_HOME_DIR3 };
    const int highIds[] = { IDC_EDIT_HOME_HIGH1, IDC_EDIT_HOME_HIGH2, IDC_EDIT_HOME_HIGH3 };
    const int lowIds[] = { IDC_EDIT_HOME_LOW1, IDC_EDIT_HOME_LOW2, IDC_EDIT_HOME_LOW3 };
    const int accIds[] = { IDC_EDIT_HOME_ACC1, IDC_EDIT_HOME_ACC2, IDC_EDIT_HOME_ACC3 };
    const int decIds[] = { IDC_EDIT_HOME_DEC1, IDC_EDIT_HOME_DEC2, IDC_EDIT_HOME_DEC3 };
    const int distIds[] = { IDC_EDIT_HOME_DIST1, IDC_EDIT_HOME_DIST2, IDC_EDIT_HOME_DIST3 };
    for (int i = 0; i < 3; ++i)
    {
        const int y = 370 + i * 45;
        CString axisLabel; axisLabel.Format(_T("%d 轴"), i + 1);
        AddLabel(kPageManual, 3150 + i, axisLabel, 430, y, 34, 30);
        AddEdit(kPageManual, dirIds[i], L"-1", 468, y, 52, 30);
        AddEdit(kPageManual, highIds[i], L"2.0", 527, y, 58, 30);
        AddEdit(kPageManual, lowIds[i], L"0.5", 590, y, 58, 30);
        AddEdit(kPageManual, accIds[i], L"0.1", 653, y, 58, 30);
        AddEdit(kPageManual, decIds[i], L"0.1", 716, y, 58, 30);
        AddEdit(kPageManual, distIds[i], L"200000", 779, y, 80, 30);
        AddLabel(kPageManual, IDC_STATIC_HOME_DIAG_1 + i,
                 L"等待读取控制器 HOME 参数", 864, y - 6, 215, 42);
        CString confirmText; confirmText.Format(_T("已核对 %d 轴"), i + 1);
        AddCheck(kPageManual, IDC_CHECK_HOME_CONFIRMED_1 + i, confirmText,
                 1084, y, 116, 30, false);
    }
    AddLabel(kPageManual, IDC_STATIC_HOME_RAW,
             L"HOME 诊断：初始化后读取触发器、触发沿、原始输入及限位状态。", 430, 500, 755, 24);
    AddButton(kPageManual, IDC_BTN_HOME_DIAG, L"读取 HOME 状态", 430, 531, 145, 38);
    AddButton(kPageManual, IDC_BTN_HOME, L"所选轴 HOME", 583, 531, 145, 38);
    AddButton(kPageManual, IDC_BTN_HOME_SEQUENCE_MANUAL, L"三轴回零 3→1→2", 736, 531, 150, 38);
    AddButton(kPageManual, IDC_BTN_HOME_RESET_MANUAL, L"回零并复位输出", 894, 531, 155, 38);
    AddButton(kPageManual, IDC_BTN_CLEAR_ALARMS, L"清报警/联锁", 1057, 531, 143, 38);
    AddButton(kPageManual, IDC_BTN_ZERO_AXIS, L"所选轴指令坐标清零", 45, 470, 250, 42);
    AddLabel(kPageManual, 3155, L"指令坐标清零不等于机械回零。HOME 参数以控制器读取值为准；错误 8 表示搜索阶段未捕获 HOME。", 45, 594, 1120, 35);
    AddGroup(kPageManual, IDC_STATIC_HOME_OVERRIDE_GROUP, L"HOME 捕获参数覆盖 | 默认沿用控制器配置", 24, 640, 1180, 165);
    AddLabel(kPageManual, IDC_STATIC_HOME_OVERRIDE_AXIS, L"轴", 45, 668, 80, 24);
    AddLabel(kPageManual, IDC_STATIC_HOME_OVERRIDE_TRIGGER, L"HOME 触发器", 150, 668, 180, 24);
    AddLabel(kPageManual, IDC_STATIC_HOME_OVERRIDE_EDGE, L"捕获沿", 440, 668, 150, 24);
    AddLabel(kPageManual, IDC_STATIC_HOME_OVERRIDE_NOTE, L"触发器 -1 表示按回零轴号匹配；捕获沿：0 下降沿，1 上升沿。", 650, 668, 500, 24);
    const int triggerComboIds[] = {
        IDC_COMBO_HOME_TRIGGER_1, IDC_COMBO_HOME_TRIGGER_2, IDC_COMBO_HOME_TRIGGER_3
    };
    const int edgeComboIds[] = {
        IDC_COMBO_HOME_EDGE_1, IDC_COMBO_HOME_EDGE_2, IDC_COMBO_HOME_EDGE_3
    };
    for (int i = 0; i < 3; ++i)
    {
        const int y = 696 + i * 32;
        CString axisName; axisName.Format(_T("%d 轴"), i + 1);
        AddLabel(kPageManual, IDC_STATIC_HOME_OVERRIDE_ROW_1 + i, axisName, 45, y, 80, 26);
        HWND triggerCombo = AddControl(kPageManual, triggerComboIds[i], L"COMBOBOX", L"",
            CBS_DROPDOWNLIST | WS_VSCROLL | WS_TABSTOP, 150, y, 240, 150);
        ::SendMessageW(triggerCombo, CB_ADDSTRING, 0, (LPARAM)L"沿用控制器配置");
        ::SendMessageW(triggerCombo, CB_ADDSTRING, 0, (LPARAM)L"按轴号匹配 (-1)");
        ::SendMessageW(triggerCombo, CB_SETCURSEL, 0, 0);
        HWND edgeCombo = AddControl(kPageManual, edgeComboIds[i], L"COMBOBOX", L"",
            CBS_DROPDOWNLIST | WS_VSCROLL | WS_TABSTOP, 440, y, 180, 150);
        ::SendMessageW(edgeCombo, CB_ADDSTRING, 0, (LPARAM)L"沿用控制器配置");
        ::SendMessageW(edgeCombo, CB_ADDSTRING, 0, (LPARAM)L"下降沿 (0)");
        ::SendMessageW(edgeCombo, CB_ADDSTRING, 0, (LPARAM)L"上升沿 (1)");
        ::SendMessageW(edgeCombo, CB_SETCURSEL, 0, 0);
    }

    // IO page.
    AddGroup(kPageIo, 3160, L"GTS-800 数字输出", 24, 94, 590, 476);
    AddGroup(kPageIo, 3161, L"gLink200 扩展输出", 630, 94, 575, 210);
    const int outYs[] = { 122, 170, 218, 266, 314, 362, 410, 458 };
    for (int i = 0; i < 8; ++i)
        AddIoRow(i, i, kOutputNames[i], kPageIo, 42, outYs[i], false);
    const int extYs[] = { 122, 170, 218 };
    for (int i = 8; i < kOutputCount; ++i)
        AddIoRow(i, i, kOutputNames[i], kPageIo, 648, extYs[i - 8], true);
    AddGroup(kPageIo, 3162, L"输入状态 | 绿色表示输入有效", 630, 322, 575, 248);
    for (int i = 0; i < (int)_countof(kDirectInputBits); ++i)
    {
        const int col = i / 4;
        const int row = i % 4;
        const int x = 650 + col * 270;
        const int y = 348 + row * 44;
        AddLabel(kPageIo, IDC_DI_STATUS_BASE + i, kDirectInputNames[i], x, y, 180, 32);
        AddLabel(kPageIo, IDC_DI_STATUS_BASE + 10 + i, L"--", x + 184, y, 52, 32);
        m_inputBitNumbers.push_back(kDirectInputBits[i]);
        m_inputStatusIds.push_back(IDC_DI_STATUS_BASE + 10 + i);
    }
    for (int i = 0; i < (int)_countof(kExtensionInputBits); ++i)
    {
        const int col = i / 6;
        const int row = i % 6;
        const int x = 42 + col * 270;
        const int y = 594 + row * 24;
        AddLabel(kPageIo, IDC_EXT_DI_STATUS_BASE + i, kExtensionInputNames[i], x, y, 220, 23);
        AddLabel(kPageIo, IDC_EXT_DI_STATUS_BASE + 12 + i, L"--", x + 222, y, 45, 23);
        m_extInputBitNumbers.push_back(kExtensionInputBits[i]);
        m_extInputStatusIds.push_back(IDC_EXT_DI_STATUS_BASE + 12 + i);
    }
    AddLabel(kPageIo, IDC_STATIC_EXI1_DIAG, L"EXI1 系统停止：原始 --；--有效；--", 650, 522, 535, 22);
    AddLabel(kPageIo, IDC_STATIC_EXI4_DIAG, L"EXI4 光幕：原始 --；--有效；--", 650, 546, 535, 22);
    AddButton(kPageIo, IDC_BTN_IO_REFRESH_PAGE, L"立即刷新 IO", 1000, 590, 175, 36);
    AddCheck(kPageIo, IDC_CHECK_DEMO_CURTAIN, L"演示：模拟光幕触发", 1000, 635, 190, 32, false);
    AddCheck(kPageIo, IDC_CHECK_DEMO_RODLESS, L"演示：模拟 DI0 到位", 1000, 674, 190, 30, true);
    AddCheck(kPageIo, IDC_CHECK_DEMO_STOP, L"演示：模拟系统停止", 1000, 710, 190, 30, false);
    AddLabel(kPageIo, 3163, L"触发后停止任务并锁止动作；需安全输入恢复后显式清报警。", 650, 676, 330, 32);

    // Automation page.
    AddGroup(kPageAuto, 3170, L"示教位置 | 点动到位后点击记录，坐标以控制器 pulse 为单位", 24, 94, 1180, 180);
    AddButton(kPageAuto, IDC_BTN_TEACH_PICK, L"记录抓取位", 48, 137, 165, 40);
    AddButton(kPageAuto, IDC_BTN_TEACH_PLACE, L"记录放置位（2层1号位）", 235, 137, 240, 40);
    AddButton(kPageAuto, IDC_BTN_TEACH_SAFE, L"记录安全零位", 497, 137, 185, 40);
    AddLabel(kPageAuto, IDC_STATIC_CAPTURE_PICK, L"抓取位：未示教", 48, 198, 340, 28);
    AddLabel(kPageAuto, IDC_STATIC_CAPTURE_PLACE, L"放置位：未示教", 420, 198, 340, 28);
    AddLabel(kPageAuto, IDC_STATIC_CAPTURE_SAFE, L"安全零位：未示教", 792, 198, 370, 28);
    AddGroup(kPageAuto, 3171, L"單次抓取、放置、回安全位", 24, 294, 1180, 350);
    AddLabel(kPageAuto, 3172, L"1 绿灯提示 → 2 无杆气缸伸出并等待 DI0 → 3 二层气缸推出 → 4 三轴移动抓取并夹紧/吸附", 50, 335, 1135, 32);
    AddLabel(kPageAuto, 3173, L"5 移至二层 1 号放置位并释放 → 6 二层复位 → 7 无杆气缸复位并等待 DI0/DI1 → 8 回安全位 → 9 绿灯关闭", 50, 379, 1135, 32);
    AddLabel(kPageAuto, 3174, L"气缸动作延时 (ms)", 52, 437, 165, 28);
    AddEdit(kPageAuto, IDC_EDIT_CYLINDER_DWELL, L"800", 220, 435, 100, 32);
    AddLabel(kPageAuto, 3175, L"等待无杆 DI0 超时 (ms)", 354, 437, 210, 28);
    AddEdit(kPageAuto, IDC_EDIT_RODLESS_TIMEOUT, L"10000", 567, 435, 110, 32);
    AddButton(kPageAuto, IDC_BTN_AUTO_START_PAGE, L"启动一次完整抓放周期", 50, 504, 260, 50);
    AddButton(kPageAuto, IDC_BTN_STOP_AUTO_PAGE, L"停止当前流程", 332, 504, 190, 50);
    AddLabel(kPageAuto, 3176, L"二层气缸没有独立行程反馈，仅按输出指令和设定延时处理；无杆气缸使用 DI0/DI1 确认对应端位。", 50, 580, 1110, 42);

    // Trajectory page.
    AddGroup(kPageTrajectory, 3180, L"坐标系默认映射：1=X、2=Y、3=Z | 所有位置单位为 pulse", 24, 94, 1180, 160);
    AddLabel(kPageTrajectory, 3181, L"目标 X", 48, 130, 95, 28); AddEdit(kPageTrajectory, IDC_EDIT_TARGET_X, L"0", 140, 128, 120, 32);
    AddLabel(kPageTrajectory, 3182, L"目标 Y", 292, 130, 95, 28); AddEdit(kPageTrajectory, IDC_EDIT_TARGET_Y, L"0", 386, 128, 120, 32);
    AddLabel(kPageTrajectory, 3183, L"目标 Z", 538, 130, 95, 28); AddEdit(kPageTrajectory, IDC_EDIT_TARGET_Z, L"0", 632, 128, 120, 32);
    AddLabel(kPageTrajectory, 3184, L"速度", 780, 130, 70, 28); AddEdit(kPageTrajectory, IDC_EDIT_TRAJ_SPEED, L"1.0", 850, 128, 100, 32);
    AddLabel(kPageTrajectory, 3185, L"加速度", 978, 130, 80, 28); AddEdit(kPageTrajectory, IDC_EDIT_TRAJ_ACC, L"0.1", 1060, 128, 100, 32);
    AddGroup(kPageTrajectory, 3186, L"圆弧/图形参数", 24, 272, 1180, 125);
    AddLabel(kPageTrajectory, 3187, L"圆心 X", 48, 313, 95, 28); AddEdit(kPageTrajectory, IDC_EDIT_CENTER_X, L"0", 140, 311, 120, 32);
    AddLabel(kPageTrajectory, 3188, L"圆心 Y", 292, 313, 95, 28); AddEdit(kPageTrajectory, IDC_EDIT_CENTER_Y, L"0", 386, 311, 120, 32);
    AddLabel(kPageTrajectory, 3189, L"半径", 538, 313, 95, 28); AddEdit(kPageTrajectory, IDC_EDIT_RADIUS, L"1000", 632, 311, 120, 32);
    AddLabel(kPageTrajectory, 3190, L"圆弧终点使用上方 X/Y；Z 保持当前位置。", 780, 313, 370, 28);
    AddButton(kPageTrajectory, IDC_BTN_TRAJ_LINE, L"创建坐标系并直线插补", 48, 435, 245, 48);
    AddButton(kPageTrajectory, IDC_BTN_TRAJ_ARC, L"圆弧插补", 313, 435, 180, 48);
    AddButton(kPageTrajectory, IDC_BTN_TRAJ_TRIANGLE, L"正三角形轨迹", 513, 435, 200, 48);
    AddButton(kPageTrajectory, IDC_BTN_TRAJ_CIRCLE, L"圆形轨迹", 733, 435, 180, 48);
    AddLabel(kPageTrajectory, 3191, L"轨迹执行要求三轴已使能且完成 HOME；运行前请确认运动范围、软限位和机械干涉。", 48, 510, 1110, 42);

    // Settings and diagnostics page.
    AddGroup(kPageSettings, 3192, L"安全输入极性与气缸输出配置", 24, 94, 690, 338);
    AddCheck(kPageSettings, IDC_CHECK_LIGHT_ACTIVE, L"光幕 EXI4：高电平有效", 50, 130, 290, 30, true);
    AddCheck(kPageSettings, IDC_CHECK_STOP_ACTIVE, L"系统停止 EXI1：高电平有效", 50, 172, 330, 30, true);
    AddCheck(kPageSettings, IDC_CHECK_POLARITY_PRESS, L"压缸 DO10：高电平伸出", 50, 210, 320, 28, true);
    AddCheck(kPageSettings, IDC_CHECK_POLARITY_RODLESS, L"无杆气缸 DO0：高电平伸出", 50, 240, 330, 28, true);
    AddCheck(kPageSettings, IDC_CHECK_POLARITY_BIN2, L"二层气缸 DO1：高电平推出", 50, 270, 330, 28, true);
    AddCheck(kPageSettings, IDC_CHECK_POLARITY_BIN3, L"三层气缸 DO2：高电平推出", 50, 300, 330, 28, true);
    AddCheck(kPageSettings, IDC_CHECK_RODLESS_ACTIVE, L"无杆到位 DI0：高电平有效", 50, 332, 330, 28, true);
    AddCheck(kPageSettings, IDC_CHECK_RODLESS_HOME_ACTIVE, L"无杆原位 DI1：高电平有效", 50, 362, 330, 28, true);
    AddCheck(kPageSettings, IDC_CHECK_RESET_PRESS, L"复位时压缸伸出", 390, 210, 300, 28, false);
    AddCheck(kPageSettings, IDC_CHECK_RESET_RODLESS, L"复位时无杆气缸伸出", 390, 240, 300, 28, false);
    AddCheck(kPageSettings, IDC_CHECK_RESET_BIN2, L"复位时二层气缸伸出", 390, 270, 300, 28, false);
    AddCheck(kPageSettings, IDC_CHECK_RESET_BIN3, L"复位时三层气缸伸出", 390, 300, 300, 28, false);
    AddCheck(kPageSettings, IDC_CHECK_POLARITY, L"本次启动已核对实物极性与复位状态", 390, 332, 300, 28, false);
    AddButton(kPageSettings, IDC_BTN_APPLY_SAFETY_POLARITY, L"应用安全输入极性", 50, 385, 245, 34);
    AddGroup(kPageSettings, 3193, L"联机诊断与工程说明", 738, 94, 466, 340);
    AddLabel(kPageSettings, 3194, L"控制卡：GTS-800-PG | 工程目标：Win32/x86", 758, 130, 410, 30);
    AddLabel(kPageSettings, 3195, L"扩展模块：type=3 / address=0，配置文件 ExtMdl.cfg", 758, 170, 410, 38);
    AddLabel(kPageSettings, 3196, L"HOME 错误 8：搜索阶段没有捕获 HOME 输入。", 758, 218, 410, 35);
    AddLabel(kPageSettings, 3197, L"无编码器反馈：指令位置不能确认丢步或机械实际位置。", 758, 260, 410, 42);
    AddLabel(kPageSettings, 3198, L"模拟模式完全隔离控制卡 API 和真实 IO。", 758, 310, 410, 34);
    AddLabel(kPageSettings, 3201, L"X/Y/Z 轴映射", 758, 346, 105, 25);
    const int mapIds[] = { IDC_COMBO_AXIS_X, IDC_COMBO_AXIS_Y, IDC_COMBO_AXIS_Z };
    const wchar_t* mapNames[] = { L"X", L"Y", L"Z" };
    for (int i = 0; i < 3; ++i)
    {
        AddLabel(kPageSettings, 3202 + i, mapNames[i], 864 + i * 105, 346, 22, 25);
        HWND mapCombo = AddControl(kPageSettings, mapIds[i], L"COMBOBOX", L"",
                                   CBS_DROPDOWNLIST | WS_VSCROLL | WS_TABSTOP,
                                   888 + i * 105, 344, 78, 180);
        ::SendMessageW(mapCombo, CB_ADDSTRING, 0, (LPARAM)L"1 轴");
        ::SendMessageW(mapCombo, CB_ADDSTRING, 0, (LPARAM)L"2 轴");
        ::SendMessageW(mapCombo, CB_ADDSTRING, 0, (LPARAM)L"3 轴");
        ::SendMessageW(mapCombo, CB_SETCURSEL, m_axisForXyz[i] - 1, 0);
    }
    AddGroup(kPageSettings, 3199, L"维护动作", 24, 450, 1180, 210);
    AddButton(kPageSettings, IDC_BTN_CLEAR_ALARMS_SETTINGS, L"清报警/解除软件联锁", 50, 494, 240, 44);
    AddButton(kPageSettings, IDC_BTN_ZERO_AXIS_SETTINGS, L"所选轴指令坐标清零", 310, 494, 240, 44);
    AddButton(kPageSettings, IDC_BTN_RESET_OUTPUTS_PAGE, L"仅复位灯/气缸输出", 570, 494, 240, 44);
    AddCheck(kPageSettings, IDC_CHECK_DEMO_CURTAIN_SETTINGS, L"演示：模拟光幕触发", 830, 494, 300, 32, false);
    AddCheck(kPageSettings, IDC_CHECK_DEMO_STOP_SETTINGS, L"演示：模拟系统停止", 830, 530, 300, 32, false);
    AddLabel(kPageSettings, 3200, L"安全极性应用不清除联锁；清报警前必须确认 EXI1 与 EXI4 均未触发。气缸复位默认收回，二层/三层无行程反馈。", 50, 570, 1110, 42);

    // Restore persisted machine settings after all runtime controls exist.
    const int persistedDirIds[] = { 0, IDC_EDIT_HOME_DIR1, IDC_EDIT_HOME_DIR2, IDC_EDIT_HOME_DIR3 };
    const int persistedHighIds[] = { 0, IDC_EDIT_HOME_HIGH1, IDC_EDIT_HOME_HIGH2, IDC_EDIT_HOME_HIGH3 };
    const int persistedLowIds[] = { 0, IDC_EDIT_HOME_LOW1, IDC_EDIT_HOME_LOW2, IDC_EDIT_HOME_LOW3 };
    const int persistedAccIds[] = { 0, IDC_EDIT_HOME_ACC1, IDC_EDIT_HOME_ACC2, IDC_EDIT_HOME_ACC3 };
    const int persistedDecIds[] = { 0, IDC_EDIT_HOME_DEC1, IDC_EDIT_HOME_DEC2, IDC_EDIT_HOME_DEC3 };
    const int persistedDistIds[] = { 0, IDC_EDIT_HOME_DIST1, IDC_EDIT_HOME_DIST2, IDC_EDIT_HOME_DIST3 };
    const int persistedTriggerIds[] = { 0, IDC_COMBO_HOME_TRIGGER_1, IDC_COMBO_HOME_TRIGGER_2, IDC_COMBO_HOME_TRIGGER_3 };
    const int persistedEdgeIds[] = { 0, IDC_COMBO_HOME_EDGE_1, IDC_COMBO_HOME_EDGE_2, IDC_COMBO_HOME_EDGE_3 };
    for (int axis = 1; axis <= 3; ++axis)
    {
        CString value;
        value.Format(_T("%d"), m_homeSettings[axis].direction); SetDlgItemText(persistedDirIds[axis], value);
        value.Format(_T("%.3f"), m_homeSettings[axis].highVel); SetDlgItemText(persistedHighIds[axis], value);
        value.Format(_T("%.3f"), m_homeSettings[axis].lowVel); SetDlgItemText(persistedLowIds[axis], value);
        value.Format(_T("%.3f"), m_homeSettings[axis].acc); SetDlgItemText(persistedAccIds[axis], value);
        value.Format(_T("%.3f"), m_homeSettings[axis].dec); SetDlgItemText(persistedDecIds[axis], value);
        value.Format(_T("%ld"), m_homeSettings[axis].searchDistance); SetDlgItemText(persistedDistIds[axis], value);
        ::SendMessageW(FindControlHwnd(persistedTriggerIds[axis]), CB_SETCURSEL,
                       m_homeSettings[axis].overrideTriggerIndex ? 1 : 0, 0);
        ::SendMessageW(FindControlHwnd(persistedEdgeIds[axis]), CB_SETCURSEL,
                       m_homeSettings[axis].overrideEdge ? (m_homeSettings[axis].edge + 1) : 0, 0);
    }
    CString dwell; dwell.Format(_T("%lu"), (unsigned long)m_cylinderDwellMs);
    SetDlgItemText(IDC_EDIT_CYLINDER_DWELL, dwell);
    CString timeout; timeout.Format(_T("%lu"), (unsigned long)m_rodlessTimeoutMs);
    SetDlgItemText(IDC_EDIT_RODLESS_TIMEOUT, timeout);
    CheckDlgButton(IDC_CHECK_LIGHT_ACTIVE, m_lightCurtainActiveHigh ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_STOP_ACTIVE, m_stopInputActiveHigh ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_POLARITY_PRESS, m_extendLevelHigh[0] ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_POLARITY_RODLESS, m_extendLevelHigh[1] ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_POLARITY_BIN2, m_extendLevelHigh[2] ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_POLARITY_BIN3, m_extendLevelHigh[3] ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_RESET_PRESS, m_resetExtend[0] ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_RESET_RODLESS, m_resetExtend[1] ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_RESET_BIN2, m_resetExtend[2] ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_RESET_BIN3, m_resetExtend[3] ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_POLARITY, m_polarityConfirmed ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_RODLESS_ACTIVE, m_rodlessInPositionActiveHigh ? BST_CHECKED : BST_UNCHECKED);
    CheckDlgButton(IDC_CHECK_RODLESS_HOME_ACTIVE, m_rodlessHomeActiveHigh ? BST_CHECKED : BST_UNCHECKED);
    if (m_demoMode) ::SendMessageW(FindControlHwnd(IDC_COMBO_MODE), CB_SETCURSEL, 1, 0);
    CString teachLabel;
    const int teachIds[] = { 0, IDC_STATIC_CAPTURE_PICK, IDC_STATIC_CAPTURE_PLACE, IDC_STATIC_CAPTURE_SAFE };
    const wchar_t* teachNames[] = { L"", L"抓取位", L"放置位", L"安全零位" };
    for (int slot = GTS_CAPTURE_PICK; slot <= GTS_CAPTURE_SAFE; ++slot)
    {
        if (!m_taught[slot]) teachLabel.Format(_T("%s：未示教"), teachNames[slot]);
        else teachLabel.Format(_T("%s：X=%ld  Y=%ld  Z=%ld pulse"), teachNames[slot],
                               m_taughtPositions[slot][1], m_taughtPositions[slot][2],
                               m_taughtPositions[slot][3]);
        SetDlgItemText(teachIds[slot], teachLabel);
    }
    ApplyPageVisibility(m_activePage);
    RECT client = {};
    GetClientRect(&client);
    LayoutUi(client.right - client.left, client.bottom - client.top);
}

void CTrapDemoMFCDlg::InitAxisStatusList()
{
    m_axisStatusList.SetExtendedStyle(LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES | LVS_EX_DOUBLEBUFFER);
    m_axisStatusList.InsertColumn(0, _T("轴号"), LVCFMT_CENTER, 70);
    m_axisStatusList.InsertColumn(1, _T("伺服"), LVCFMT_CENTER, 105);
    m_axisStatusList.InsertColumn(2, _T("运动"), LVCFMT_CENTER, 105);
    m_axisStatusList.InsertColumn(3, _T("正限位"), LVCFMT_CENTER, 105);
    m_axisStatusList.InsertColumn(4, _T("负限位"), LVCFMT_CENTER, 105);
    m_axisStatusList.InsertColumn(5, _T("报警"), LVCFMT_CENTER, 105);
    m_axisStatusList.InsertColumn(6, _T("指令位置 (pulse)"), LVCFMT_RIGHT, 190);
    for (int i = 0; i < 3; ++i)
    {
        CString axisName; axisName.Format(_T("%d 轴"), i + 1);
        int row = m_axisStatusList.InsertItem(i, axisName);
        for (int col = 1; col < 7; ++col) m_axisStatusList.SetItemText(row, col, _T("--"));
    }
}

void CTrapDemoMFCDlg::ApplyPageVisibility(int page)
{
    if (page < 0 || page >= 6) page = kPageOverview;
    if (m_activePage != page &&
        InterlockedCompareExchange(&m_activeCommand, 0, 0) == GTS_CMD_JOG)
    {
        InterlockedExchange(&m_stopRequested, 1);
        const HWND capture = ::GetCapture();
        if (capture == m_btnJogNegative.GetSafeHwnd() ||
            capture == m_btnJogPositive.GetSafeHwnd())
            ::ReleaseCapture();
        AppendLogUi(L"切换分页，已请求停止按住点动。");
    }
    m_activePage = page;
    for (int i = 0; i < 6; ++i)
    {
        if (!m_pageViewports[i].GetSafeHwnd()) continue;
        m_pageViewports[i].ShowWindow(i == page ? SW_SHOW : SW_HIDE);
        if (i == page) m_pageViewports[i].ResetScroll();
    }
    if (m_tab.GetSafeHwnd()) m_tab.Invalidate(FALSE);
}

void CTrapDemoMFCDlg::LayoutUi(int width, int height)
{
    if (width <= 0 || height <= 0) return;
    const double scale = (double)DpiForWindow(m_hWnd) / 96.0;
    const int clientWidth = max(1, (int)(width / scale));
    const int clientHeight = max(1, (int)(height / scale));
    const int margin = 14;
    auto scaled = [scale](int value) { return max(1, (int)(value * scale + 0.5)); };

    auto move = [this, &scaled](int id, int x, int y, int w, int h)
    {
        HWND hwnd = ::GetDlgItem(m_hWnd, id);
        if (::IsWindow(hwnd)) ::MoveWindow(hwnd, scaled(x), scaled(y), scaled(w), scaled(h), TRUE);
    };

    // Reflow the fixed header into two status rows and one compact command row.
    move(m_controllerStatusId, margin, 7, 205, 23);
    move(m_extensionStatusId, margin + 210, 7, 205, 23);
    move(IDC_STATIC_FEEDBACK, margin, 30, 235, 22);
    move(m_hardwareStatusId, margin + 240, 30, max(150, clientWidth - margin * 2 - 430), 22);
    move(3090, max(margin + 430, clientWidth - 158), 7, 48, 23);
    move(IDC_COMBO_MODE, max(margin + 480, clientWidth - 112), 6, 98, 200);

    const int cmdY = 53;
    int x = margin;
    move(IDC_BTN_INIT, x, cmdY, 82, 30); x += 88;
    move(IDC_BTN_ENABLE, x, cmdY, 88, 30); x += 94;
    move(IDC_BTN_DISABLE, x, cmdY, 88, 30); x += 94;
    move(IDC_BTN_STOP, x, cmdY, 112, 30); x += 118;
    move(IDC_CHECK_OPERATOR_SAFE, x, cmdY, 178, 30); x += 184;
    move(m_progressLabelId, margin, 84, max(100, clientWidth - margin * 2), 20);

    const int tabTop = 108;
    const int tabHeight = max(150, clientHeight - tabTop - 70);
    move(IDC_TAB_MAIN, margin, tabTop, max(200, clientWidth - margin * 2), tabHeight);

    // Keep the log docked while allowing the tab content to use the remaining space.
    const int logLabelY = max(tabTop + 10, clientHeight - 70);
    const int logY = clientHeight - 50;
    const int rightColumn = 126;
    move(3091, margin, logLabelY, 90, 19);
    move(IDC_EDIT_LOG_NEW, margin, logY,
         max(240, clientWidth - margin * 2 - rightColumn), 43);
    move(IDC_CHECK_LOG_AUTOSCROLL, max(margin, clientWidth - margin - 126),
         logY, 126, 22);
    move(IDC_BTN_CLEAR_LOG, max(margin, clientWidth - margin - 126),
         logY + 23, 126, 23);

    if (m_tab.GetSafeHwnd())
    {
        CRect pageRect;
        m_tab.GetClientRect(&pageRect);
        m_tab.AdjustRect(FALSE, &pageRect);
        m_tab.ClientToScreen(&pageRect);
        ScreenToClient(&pageRect);
        for (int page = 0; page < 6; ++page)
        {
            CPageViewport& viewport = m_pageViewports[page];
            if (!viewport.GetSafeHwnd()) continue;
            viewport.MoveWindow(&pageRect, TRUE);
            viewport.SetLayoutScale(scale);
            int contentWidth = 1;
            int contentHeight = 1;
            for (size_t i = 0; i < m_layoutEntries.size(); ++i)
            {
                const LayoutEntry& entry = m_layoutEntries[i];
                if (entry.page != page || !::IsWindow(entry.hwnd)) continue;
                contentWidth = max(contentWidth, scaled(entry.rect.right) + scaled(8));
                contentHeight = max(contentHeight, scaled(entry.rect.bottom) + scaled(8));
            }
            viewport.SetContentSize(contentWidth, contentHeight);
        }
    }
}

void CTrapDemoMFCDlg::OnSize(UINT nType, int cx, int cy)
{
    CDialogEx::OnSize(nType, cx, cy);
    if (!m_layoutEntries.empty()) LayoutUi(cx, cy);
}

void CTrapDemoMFCDlg::OnGetMinMaxInfo(MINMAXINFO* pMMI)
{
    CDialogEx::OnGetMinMaxInfo(pMMI);
    const int scale = (int)DpiForWindow(m_hWnd);
    pMMI->ptMinTrackSize.x = ::MulDiv(640, scale, 96);
    pMMI->ptMinTrackSize.y = ::MulDiv(500, scale, 96);
}

void CTrapDemoMFCDlg::OnTabChanged(NMHDR*, LRESULT* pResult)
{
    ApplyPageVisibility(m_tab.GetCurSel());
    if (pResult) *pResult = 0;
}

CWnd* CTrapDemoMFCDlg::GetDlgItem(int nID) const
{
    CWnd* item = CDialogEx::GetDlgItem(nID);
    if (item) return item;
    for (int i = 0; i < 6; ++i)
    {
        item = const_cast<CPageViewport&>(m_pageViewports[i]).GetDlgItem(nID);
        if (item) return item;
    }
    return NULL;
}

int CTrapDemoMFCDlg::GetDlgItemText(int nID, CString& text) const
{
    CWnd* item = GetDlgItem(nID);
    if (!item) { text.Empty(); return 0; }
    item->GetWindowText(text);
    return text.GetLength();
}

UINT CTrapDemoMFCDlg::IsDlgButtonChecked(int nID) const
{
    CWnd* item = GetDlgItem(nID);
    return item ? (UINT)item->SendMessage(BM_GETCHECK, 0, 0) : BST_UNCHECKED;
}

void CTrapDemoMFCDlg::CheckDlgButton(int nID, UINT state)
{
    CWnd* item = GetDlgItem(nID);
    if (item) item->SendMessage(BM_SETCHECK, state, 0);
}

BOOL CTrapDemoMFCDlg::SetDlgItemText(int nID, LPCTSTR text)
{
    CWnd* item = GetDlgItem(nID);
    if (!item) return FALSE;
    item->SetWindowText(text);
    return TRUE;
}

HWND CTrapDemoMFCDlg::FindControlHwnd(int nID) const
{
    CWnd* item = GetDlgItem(nID);
    return item ? item->GetSafeHwnd() : NULL;
}

CString CTrapDemoMFCDlg::SettingsPath() const
{
    wchar_t path[MAX_PATH] = {};
    ::GetModuleFileNameW(NULL, path, _countof(path));
    wchar_t* slash = wcsrchr(path, L'\\');
    if (slash) *(slash + 1) = L'\0';
    CString result(path);
    result += _T("machine_settings.ini");
    return result;
}

void CTrapDemoMFCDlg::LoadSettings()
{
    const CString path = SettingsPath();
    m_demoMode = ::GetPrivateProfileIntW(L"General", L"DemoMode", 0, path) != 0;
    // A hardware confirmation is session-scoped and must be repeated after restart.
    m_polarityConfirmed = false;
    m_lightCurtainActiveHigh = ::GetPrivateProfileIntW(L"Safety", L"LightCurtainActiveHigh", 1, path) != 0;
    m_stopInputActiveHigh = ::GetPrivateProfileIntW(L"Safety", L"StopInputActiveHigh", 1, path) != 0;
    m_rodlessInPositionActiveHigh = ::GetPrivateProfileIntW(L"Safety", L"RodlessInPositionActiveHigh", 1, path) != 0;
    m_rodlessHomeActiveHigh = ::GetPrivateProfileIntW(L"Safety", L"RodlessHomeActiveHigh", 1, path) != 0;
    InterlockedExchange(&m_simExtInputs, m_rodlessInPositionActiveHigh ? 1 : 0);
    m_axisForXyz[0] = (short)::GetPrivateProfileIntW(L"Coordinates", L"XAxis", 1, path);
    m_axisForXyz[1] = (short)::GetPrivateProfileIntW(L"Coordinates", L"YAxis", 2, path);
    m_axisForXyz[2] = (short)::GetPrivateProfileIntW(L"Coordinates", L"ZAxis", 3, path);
    bool mapOk = true, seen[4] = {};
    for (int i = 0; i < 3; ++i)
    {
        if (m_axisForXyz[i] < 1 || m_axisForXyz[i] > 3 || seen[m_axisForXyz[i]]) mapOk = false;
        else seen[m_axisForXyz[i]] = true;
    }
    if (!mapOk) { m_axisForXyz[0] = 1; m_axisForXyz[1] = 2; m_axisForXyz[2] = 3; }
    m_cylinderDwellMs = (DWORD)::GetPrivateProfileIntW(L"Automation", L"CylinderDwellMs", 800, path);
    m_rodlessTimeoutMs = (DWORD)::GetPrivateProfileIntW(L"Automation", L"RodlessTimeoutMs", 10000, path);
    m_extendLevelHigh[0] = ::GetPrivateProfileIntW(L"IO", L"PressExtendHigh", 1, path) != 0;
    m_extendLevelHigh[1] = ::GetPrivateProfileIntW(L"IO", L"RodlessExtendHigh", 1, path) != 0;
    m_extendLevelHigh[2] = ::GetPrivateProfileIntW(L"IO", L"Bin2ExtendHigh", 1, path) != 0;
    m_extendLevelHigh[3] = ::GetPrivateProfileIntW(L"IO", L"Bin3ExtendHigh", 1, path) != 0;
    m_resetExtend[0] = ::GetPrivateProfileIntW(L"IO", L"ResetPressExtended", 0, path) != 0;
    m_resetExtend[1] = ::GetPrivateProfileIntW(L"IO", L"ResetRodlessExtended", 0, path) != 0;
    m_resetExtend[2] = ::GetPrivateProfileIntW(L"IO", L"ResetBin2Extended", 0, path) != 0;
    m_resetExtend[3] = ::GetPrivateProfileIntW(L"IO", L"ResetBin3Extended", 0, path) != 0;

    const int dirIds[] = { IDC_EDIT_HOME_DIR1, IDC_EDIT_HOME_DIR2, IDC_EDIT_HOME_DIR3 };
    const int highIds[] = { IDC_EDIT_HOME_HIGH1, IDC_EDIT_HOME_HIGH2, IDC_EDIT_HOME_HIGH3 };
    const int lowIds[] = { IDC_EDIT_HOME_LOW1, IDC_EDIT_HOME_LOW2, IDC_EDIT_HOME_LOW3 };
    const int accIds[] = { IDC_EDIT_HOME_ACC1, IDC_EDIT_HOME_ACC2, IDC_EDIT_HOME_ACC3 };
    const int decIds[] = { IDC_EDIT_HOME_DEC1, IDC_EDIT_HOME_DEC2, IDC_EDIT_HOME_DEC3 };
    const int distIds[] = { IDC_EDIT_HOME_DIST1, IDC_EDIT_HOME_DIST2, IDC_EDIT_HOME_DIST3 };
    for (int axis = 1; axis <= 3; ++axis)
    {
        CString key;
        key.Format(L"Axis%dDirection", axis); m_homeSettings[axis].direction = ::GetPrivateProfileIntW(L"Home", key, -1, path) == 1 ? 1 : -1;
        key.Format(L"Axis%dHigh", axis); m_homeSettings[axis].highVel = ::GetPrivateProfileIntW(L"Home", key, 200, path) / 100.0;
        key.Format(L"Axis%dLow", axis); m_homeSettings[axis].lowVel = ::GetPrivateProfileIntW(L"Home", key, 50, path) / 100.0;
        key.Format(L"Axis%dAcc", axis); m_homeSettings[axis].acc = ::GetPrivateProfileIntW(L"Home", key, 1, path) / 10.0;
        key.Format(L"Axis%dDec", axis); m_homeSettings[axis].dec = ::GetPrivateProfileIntW(L"Home", key, 1, path) / 10.0;
        key.Format(L"Axis%dDistance", axis); m_homeSettings[axis].searchDistance = ::GetPrivateProfileIntW(L"Home", key, 200000, path);
        key.Format(L"Axis%dTriggerOverride", axis); m_homeSettings[axis].overrideTriggerIndex = ::GetPrivateProfileIntW(L"Home", key, 0, path) != 0;
        m_homeSettings[axis].triggerIndex = -1;
        key.Format(L"Axis%dEdgeOverride", axis); m_homeSettings[axis].overrideEdge = ::GetPrivateProfileIntW(L"Home", key, 0, path) != 0;
        key.Format(L"Axis%dEdge", axis); m_homeSettings[axis].edge = (short)(::GetPrivateProfileIntW(L"Home", key, 0, path) == 1 ? 1 : 0);
    }
    for (int slot = GTS_CAPTURE_PICK; slot <= GTS_CAPTURE_SAFE; ++slot)
    {
        CString key; key.Format(L"Taught%d", slot);
        m_taught[slot] = ::GetPrivateProfileIntW(L"Teach", key, 0, path) != 0;
    }
    for (int slot = GTS_CAPTURE_PICK; slot <= GTS_CAPTURE_SAFE; ++slot)
    {
        for (int axis = 1; axis <= 3; ++axis)
        {
            CString key; key.Format(L"Slot%dAxis%d", slot, axis);
            m_taughtPositions[slot][axis] = ::GetPrivateProfileIntW(L"Teach", key, 0, path);
        }
    }
    // Settings text controls are created later; defaults are retained in member state.
    (void)dirIds; (void)highIds; (void)lowIds; (void)accIds; (void)decIds; (void)distIds;
}

void CTrapDemoMFCDlg::SaveSettings() const
{
    const CString path = SettingsPath();
    auto writeInt = [&path](LPCWSTR section, LPCWSTR key, int value)
    {
        CString text; text.Format(L"%d", value);
        ::WritePrivateProfileStringW(section, key, text, path);
    };
    auto writeLong = [&path](LPCWSTR section, LPCWSTR key, long value)
    {
        CString text; text.Format(L"%ld", value);
        ::WritePrivateProfileStringW(section, key, text, path);
    };
    writeInt(L"General", L"DemoMode", m_demoMode ? 1 : 0);
    writeInt(L"IO", L"PressExtendHigh", m_extendLevelHigh[0] ? 1 : 0);
    writeInt(L"IO", L"RodlessExtendHigh", m_extendLevelHigh[1] ? 1 : 0);
    writeInt(L"IO", L"Bin2ExtendHigh", m_extendLevelHigh[2] ? 1 : 0);
    writeInt(L"IO", L"Bin3ExtendHigh", m_extendLevelHigh[3] ? 1 : 0);
    writeInt(L"IO", L"ResetPressExtended", m_resetExtend[0] ? 1 : 0);
    writeInt(L"IO", L"ResetRodlessExtended", m_resetExtend[1] ? 1 : 0);
    writeInt(L"IO", L"ResetBin2Extended", m_resetExtend[2] ? 1 : 0);
    writeInt(L"IO", L"ResetBin3Extended", m_resetExtend[3] ? 1 : 0);
    writeInt(L"Safety", L"LightCurtainActiveHigh", m_lightCurtainActiveHigh ? 1 : 0);
    writeInt(L"Safety", L"StopInputActiveHigh", m_stopInputActiveHigh ? 1 : 0);
    writeInt(L"Safety", L"RodlessInPositionActiveHigh", m_rodlessInPositionActiveHigh ? 1 : 0);
    writeInt(L"Safety", L"RodlessHomeActiveHigh", m_rodlessHomeActiveHigh ? 1 : 0);
    writeInt(L"Coordinates", L"XAxis", m_axisForXyz[0]);
    writeInt(L"Coordinates", L"YAxis", m_axisForXyz[1]);
    writeInt(L"Coordinates", L"ZAxis", m_axisForXyz[2]);
    writeInt(L"Automation", L"CylinderDwellMs", (int)m_cylinderDwellMs);
    writeInt(L"Automation", L"RodlessTimeoutMs", (int)m_rodlessTimeoutMs);
    for (int axis = 1; axis <= 3; ++axis)
    {
        CString key;
        key.Format(L"Axis%dDirection", axis); writeInt(L"Home", key, m_homeSettings[axis].direction);
        key.Format(L"Axis%dHigh", axis); writeInt(L"Home", key, (int)(m_homeSettings[axis].highVel * 100.0));
        key.Format(L"Axis%dLow", axis); writeInt(L"Home", key, (int)(m_homeSettings[axis].lowVel * 100.0));
        key.Format(L"Axis%dAcc", axis); writeInt(L"Home", key, (int)(m_homeSettings[axis].acc * 10.0));
        key.Format(L"Axis%dDec", axis); writeInt(L"Home", key, (int)(m_homeSettings[axis].dec * 10.0));
        key.Format(L"Axis%dDistance", axis); writeLong(L"Home", key, m_homeSettings[axis].searchDistance);
        key.Format(L"Axis%dTriggerOverride", axis); writeInt(L"Home", key, m_homeSettings[axis].overrideTriggerIndex ? 1 : 0);
        key.Format(L"Axis%dEdgeOverride", axis); writeInt(L"Home", key, m_homeSettings[axis].overrideEdge ? 1 : 0);
        key.Format(L"Axis%dEdge", axis); writeInt(L"Home", key, m_homeSettings[axis].edge);
    }
    for (int slot = GTS_CAPTURE_PICK; slot <= GTS_CAPTURE_SAFE; ++slot)
    {
        CString key; key.Format(L"Taught%d", slot); writeInt(L"Teach", key, m_taught[slot] ? 1 : 0);
        for (int axis = 1; axis <= 3; ++axis)
        {
            key.Format(L"Slot%dAxis%d", slot, axis);
            writeLong(L"Teach", key, m_taughtPositions[slot][axis]);
        }
    }
}

GtsCommandRequest CTrapDemoMFCDlg::DefaultRequest(LONG command) const
{
    GtsCommandRequest request = {};
    request.command = command;
    request.axis = 1;
    request.direction = 1;
    request.cylinderDwellMs = m_cylinderDwellMs;
    request.rodlessTimeoutMs = m_rodlessTimeoutMs;
    request.polarityConfirmed = m_polarityConfirmed;
    request.demoMode = m_demoMode;
    request.lightCurtainActiveHigh = m_lightCurtainActiveHigh;
    request.stopInputActiveHigh = m_stopInputActiveHigh;
    request.rodlessInPositionActiveHigh = m_rodlessInPositionActiveHigh;
    request.rodlessHomeActiveHigh = m_rodlessHomeActiveHigh;
    for (int i = 0; i < 3; ++i) request.axisForXyz[i] = m_axisForXyz[i];
    for (int i = 0; i < 4; ++i) request.extendLevelHigh[i] = m_extendLevelHigh[i];
    for (int i = 0; i < 4; ++i) request.resetExtend[i] = m_resetExtend[i];
    return request;
}

BOOL CTrapDemoMFCDlg::SubmitRequest(const GtsCommandRequest& request,
                                    bool resetStopFlag)
{
    if (m_pWorker == NULL || m_closing) return FALSE;
    if (InterlockedCompareExchange(&m_busy, 1, 0) != 0)
    {
        AppendLogUi(L"当前已有任务执行。请等待完成或先请求停止。");
        return FALSE;
    }
    if (request.command == GTS_CMD_INIT)
    {
        for (int axis = 1; axis <= 3; ++axis)
        {
            m_homeConfirmed[axis] = false;
            m_homeDiagnosticsReceived[axis] = false;
            ZeroMemory(&m_homeConfirmedSettings[axis], sizeof(m_homeConfirmedSettings[axis]));
            CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + axis - 1, BST_UNCHECKED);
            SetDlgItemText(IDC_STATIC_HOME_DIAG_1 + axis - 1,
                           _T("等待读取控制器 HOME 参数"));
        }
        m_homeInputReadRc = -1;
        SetDlgItemText(IDC_STATIC_HOME_RAW, _T("初始化后将读取 HOME 参数、原始输入和限位状态。"));
    }
    if (resetStopFlag) InterlockedExchange(&m_stopRequested, 0);
    m_commandLock.Lock();
    m_request = request;
    m_commandLock.Unlock();
    InterlockedExchange(&m_activeCommand, request.command);
    m_lastCommandAxis = request.axis;
    InterlockedExchange(&m_activeJogDirection,
                        request.command == GTS_CMD_JOG ? request.direction : 0);
    UpdateUiState();
    m_commandEvent.SetEvent();
    return TRUE;
}

bool CTrapDemoMFCDlg::ReadLongValue(int controlId, long& value) const
{
    CString text;
    const_cast<CTrapDemoMFCDlg*>(this)->GetDlgItemText(controlId, text);
    text.Trim();
    if (text.IsEmpty()) return false;
    TCHAR* end = NULL;
    long parsed = _tcstol(text.GetString(), &end, 10);
    if (end == text.GetString() || *end != _T('\0')) return false;
    value = parsed;
    return true;
}

bool CTrapDemoMFCDlg::ReadPositiveDouble(int controlId, double& value,
                                          double maxValue) const
{
    CString text;
    const_cast<CTrapDemoMFCDlg*>(this)->GetDlgItemText(controlId, text);
    text.Trim();
    if (text.IsEmpty()) return false;
    TCHAR* end = NULL;
    double parsed = _tcstod(text.GetString(), &end);
    if (end == text.GetString() || *end != _T('\0') || !_finite(parsed) ||
        parsed <= 0.0 || parsed > maxValue) return false;
    value = parsed;
    return true;
}

short CTrapDemoMFCDlg::SelectedAxis() const
{
    HWND hwnd = FindControlHwnd(IDC_COMBO_AXIS_NEW);
    if (!hwnd) return 1;
    int selected = (int)::SendMessageW(hwnd, CB_GETCURSEL, 0, 0);
    return selected >= 0 && selected <= 2 ? (short)(selected + 1) : 1;
}

bool CTrapDemoMFCDlg::ReadAxisMotionInputs(short axis, long& pos, double& vel) const
{
    if (axis < 1 || axis > 3) return false;
    const int posIds[4] = { 0, IDC_EDIT_POS1_NEW, IDC_EDIT_POS2_NEW, IDC_EDIT_POS3_NEW };
    const int velIds[4] = { 0, IDC_EDIT_VEL1_NEW, IDC_EDIT_VEL2_NEW, IDC_EDIT_VEL3_NEW };
    return ReadLongValue(posIds[axis], pos) && ReadPositiveDouble(velIds[axis], vel);
}

bool CTrapDemoMFCDlg::ReadCommonAccDec(double& acc, double& dec) const
{
    return ReadPositiveDouble(IDC_EDIT_ACC_NEW, acc, 100000.0) &&
           ReadPositiveDouble(IDC_EDIT_DEC_NEW, dec, 100000.0);
}

bool CTrapDemoMFCDlg::ReadHomeSettings(short axis, AxisHomeSettings& settings) const
{
    if (axis < 1 || axis > 3) return false;
    const int dirIds[4] = { 0, IDC_EDIT_HOME_DIR1, IDC_EDIT_HOME_DIR2, IDC_EDIT_HOME_DIR3 };
    const int highIds[4] = { 0, IDC_EDIT_HOME_HIGH1, IDC_EDIT_HOME_HIGH2, IDC_EDIT_HOME_HIGH3 };
    const int lowIds[4] = { 0, IDC_EDIT_HOME_LOW1, IDC_EDIT_HOME_LOW2, IDC_EDIT_HOME_LOW3 };
    const int accIds[4] = { 0, IDC_EDIT_HOME_ACC1, IDC_EDIT_HOME_ACC2, IDC_EDIT_HOME_ACC3 };
    const int decIds[4] = { 0, IDC_EDIT_HOME_DEC1, IDC_EDIT_HOME_DEC2, IDC_EDIT_HOME_DEC3 };
    const int distIds[4] = { 0, IDC_EDIT_HOME_DIST1, IDC_EDIT_HOME_DIST2, IDC_EDIT_HOME_DIST3 };
    long direction = 0, distance = 0;
    if (!ReadLongValue(dirIds[axis], direction) || (direction != -1 && direction != 1) ||
        !ReadPositiveDouble(highIds[axis], settings.highVel) ||
        !ReadPositiveDouble(lowIds[axis], settings.lowVel) ||
        settings.lowVel > settings.highVel ||
        !ReadPositiveDouble(accIds[axis], settings.acc, 100000.0) ||
        !ReadPositiveDouble(decIds[axis], settings.dec, 100000.0) ||
        !ReadLongValue(distIds[axis], distance) || distance <= 0)
        return false;
    settings.direction = (int)direction;
    settings.searchDistance = distance;
    const int triggerIds[4] = { 0, IDC_COMBO_HOME_TRIGGER_1, IDC_COMBO_HOME_TRIGGER_2, IDC_COMBO_HOME_TRIGGER_3 };
    const int edgeIds[4] = { 0, IDC_COMBO_HOME_EDGE_1, IDC_COMBO_HOME_EDGE_2, IDC_COMBO_HOME_EDGE_3 };
    const int triggerSelection = (int)::SendMessageW(FindControlHwnd(triggerIds[axis]), CB_GETCURSEL, 0, 0);
    const int edgeSelection = (int)::SendMessageW(FindControlHwnd(edgeIds[axis]), CB_GETCURSEL, 0, 0);
    if (triggerSelection < 0 || triggerSelection > 1 || edgeSelection < 0 || edgeSelection > 2)
        return false;
    settings.overrideTriggerIndex = triggerSelection == 1;
    settings.triggerIndex = -1; // SDK defines -1 as matching the HOME axis.
    settings.overrideEdge = edgeSelection != 0;
    settings.edge = edgeSelection == 0 ? 0 : (short)(edgeSelection - 1);
    settings.confirmationRequired = false;
    return true;
}

bool CTrapDemoMFCDlg::ReadAllHomeSettings(AxisHomeSettings settings[4]) const
{
    for (short axis = 1; axis <= 3; ++axis)
        if (!ReadHomeSettings(axis, settings[axis])) return false;
    return true;
}

LRESULT CTrapDemoMFCDlg::OnHomeDiagnostics(WPARAM, LPARAM lParam)
{
    GtsHomeDiagnosticsPacket* packet =
        reinterpret_cast<GtsHomeDiagnosticsPacket*>(lParam);
    if (!packet) return 0;
    m_homeInputReadRc = packet->inputRc;
    m_homeRawInputs = packet->directInputs;
    CString rawText;
    if (packet->inputRc == 0)
        rawText.Format(_T("原始 GPI=0x%08lX；HOME 触发器/沿来自控制器配置，限位与捕获状态见各轴行。"),
                       packet->directInputs);
    else
        rawText.Format(_T("HOME 原始输入读取失败（返回码 %d）；硬件 HOME 暂不可确认。"),
                       packet->inputRc);
    SetDlgItemText(IDC_STATIC_HOME_RAW, rawText);

    for (int i = 0; i < 3; ++i)
    {
        const GtsHomeDiagnosticRow& row = packet->rows[i];
        const int axis = i + 1;
        if (m_homeConfirmed[axis] && m_homeDiagnosticsReceived[axis] &&
            (m_homeTriggerIndex[axis] != row.triggerIndex ||
             m_homeTriggerEdge[axis] != row.edge ||
             m_homeControllerDirection[axis] != row.moveDir))
        {
            m_homeConfirmed[axis] = false;
            CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + i, BST_UNCHECKED);
            AppendLogUi(L"检测到控制器 HOME 触发器/沿已变化，已撤销该轴现场确认。");
        }
        m_homeTriggerIndex[axis] = row.triggerIndex;
        m_homeTriggerEdge[axis] = row.edge;
        m_homeControllerDirection[axis] = row.moveDir;
        m_homeDiagnosticsReceived[axis] =
            packet->inputRc == 0 && row.homePrmRc == 0 && row.statusRc == 0;

        CString text;
        if (row.homePrmRc != 0 || row.statusRc != 0)
            text.Format(_T("HOME参数=%d 状态=%d；不可确认"), row.homePrmRc, row.statusRc);
        else
        {
            const bool posLimit = (row.status & 0x0020) != 0;
            const bool negLimit = (row.status & 0x0040) != 0;
            text.Format(_T("Trig=%d Edge=%d Dir=%d\r\nLim=%d/%d S=%d E=%d R=%d\r\nCAP=%ld"),
                        row.triggerIndex, row.edge, row.moveDir,
                        posLimit ? 1 : 0, negLimit ? 1 : 0,
                        row.stage, row.error, row.run, row.capturePos);
        }
        SetDlgItemText(IDC_STATIC_HOME_DIAG_1 + i, text);
        if (m_demoMode || !m_homeDiagnosticsReceived[axis])
        {
            m_homeConfirmed[axis] = false;
            CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + i, BST_UNCHECKED);
        }
    }
    delete packet;
    UpdateUiState();
    return 0;
}

bool CTrapDemoMFCDlg::ReadTrajectory(GtsTrajectoryRequest& trajectory) const
{
    long x = 0, y = 0, z = 0, cx = 0, cy = 0, radius = 0;
    if (!ReadLongValue(IDC_EDIT_TARGET_X, x) || !ReadLongValue(IDC_EDIT_TARGET_Y, y) ||
        !ReadLongValue(IDC_EDIT_TARGET_Z, z) ||
        !ReadLongValue(IDC_EDIT_CENTER_X, cx) || !ReadLongValue(IDC_EDIT_CENTER_Y, cy) ||
        !ReadLongValue(IDC_EDIT_RADIUS, radius) ||
        !ReadPositiveDouble(IDC_EDIT_TRAJ_SPEED, trajectory.velocity) ||
        !ReadPositiveDouble(IDC_EDIT_TRAJ_ACC, trajectory.acceleration, 100000.0))
        return false;
    trajectory.x = x; trajectory.y = y; trajectory.z = z;
    trajectory.centerX = cx; trajectory.centerY = cy; trajectory.radius = radius;
    return true;
}

bool CTrapDemoMFCDlg::ReadRecipe(GtsPickPlaceRecipe& recipe) const
{
    if (!m_taught[GTS_CAPTURE_PICK] || !m_taught[GTS_CAPTURE_PLACE] ||
        !m_taught[GTS_CAPTURE_SAFE]) return false;
    double velocity = 0.0, acceleration = 0.0;
    if (!ReadPositiveDouble(IDC_EDIT_TRAJ_SPEED, velocity) ||
        !ReadPositiveDouble(IDC_EDIT_TRAJ_ACC, acceleration, 100000.0)) return false;
    ZeroMemory(&recipe, sizeof(recipe));
    for (short axis = 1; axis <= 3; ++axis)
    {
        recipe.pick[axis] = m_taughtPositions[GTS_CAPTURE_PICK][axis];
        recipe.place[axis] = m_taughtPositions[GTS_CAPTURE_PLACE][axis];
        recipe.safe[axis] = m_taughtPositions[GTS_CAPTURE_SAFE][axis];
        recipe.velocity[axis] = velocity;
    }
    recipe.acceleration = acceleration;
    return true;
}

bool CTrapDemoMFCDlg::OperatorConfirmed() const
{
    return IsDlgButtonChecked(IDC_CHECK_OPERATOR_SAFE) == BST_CHECKED;
}

UINT CTrapDemoMFCDlg::WorkerThreadProc(LPVOID pParam)
{
    return static_cast<CTrapDemoMFCDlg*>(pParam)->WorkerLoop();
}

UINT CTrapDemoMFCDlg::WorkerLoop()
{
    for (;;)
    {
        const BOOL signaled = m_commandEvent.Lock(200);
        if (InterlockedCompareExchange(&m_shutdown, 0, 0) != 0) break;

        if (!signaled)
        {
            if (m_demoMode)
            {
                if (m_simInitialized) { PublishDemoStatus(); PublishDemoIo(); }
            }
            else if (m_motion.IsInitialized())
            {
                m_motion.PublishAxisStatus();
                m_motion.PollIoStatus();
            }
            continue;
        }

        GtsCommandRequest request = {};
        m_commandLock.Lock();
        request = m_request;
        m_request.command = GTS_CMD_NONE;
        m_commandLock.Unlock();
        if (request.command == GTS_CMD_NONE) continue;

        short rc = 0;
        if (request.demoMode)
        {
            rc = RunDemoCommand(request);
            PublishDemoStatus();
            PublishDemoIo();
        }
        else
        {
            if (!m_motion.SetCoordinateMapping(request.axisForXyz)) rc = -103;
            else switch (request.command)
            {
            case GTS_CMD_INIT:
                rc = m_motion.Initialize(m_hWnd, request.lightCurtainActiveHigh,
                                         request.stopInputActiveHigh);
                if (rc == 0) m_motion.PublishHomeDiagnostics();
                break;
            case GTS_CMD_ENABLE:
                rc = m_motion.EnableAxes();
                break;
            case GTS_CMD_MOVE_SINGLE:
                rc = m_motion.MovePoint(request.axis, request.targets[request.axis],
                                        request.velocities[request.axis], request.acceleration,
                                        request.deceleration, &m_stopRequested);
                break;
            case GTS_CMD_SEQUENCE:
                rc = m_motion.MoveSequence(request.targets, request.velocities,
                                           request.acceleration, request.deceleration,
                                           &m_stopRequested);
                break;
            case GTS_CMD_JOG:
                rc = m_motion.JogHold(request.axis, request.direction,
                                      request.velocities[request.axis], request.acceleration,
                                      request.deceleration, &m_stopRequested);
                break;
            case GTS_CMD_HOME_AXIS:
                rc = m_motion.HomeAxis(request.axis, request.home[request.axis],
                                       &m_stopRequested);
                break;
            case GTS_CMD_HOME_SEQUENCE:
                rc = m_motion.HomeSequence(request.home, request.resetOutputs,
                                           request.extendLevelHigh, request.resetExtend,
                                           request.polarityConfirmed,
                                           &m_stopRequested);
                break;
            case GTS_CMD_CLEAR_ALARMS:
                rc = m_motion.ClearAlarms();
                break;
            case GTS_CMD_ZERO_AXIS:
                rc = m_motion.ZeroAxis(request.axis);
                break;
            case GTS_CMD_IO_OUTPUT:
                if (request.output >= GTS_OUT_PRESS_CYLINDER && !request.polarityConfirmed)
                    rc = -131;
                else
                    rc = m_motion.SetLogicalOutput(request.output, request.outputOn,
                                                   request.extendLevelHigh);
                break;
            case GTS_CMD_AUTO_PICK_PLACE:
                rc = m_motion.RunPickPlace(request.recipe, request.cylinderDwellMs,
                                           request.rodlessTimeoutMs, request.extendLevelHigh,
                                           request.resetExtend, request.polarityConfirmed,
                                           request.rodlessInPositionActiveHigh,
                                           request.rodlessHomeActiveHigh,
                                           &m_stopRequested);
                break;
            case GTS_CMD_TRAJECTORY:
                rc = m_motion.RunTrajectory(request.trajectory, &m_stopRequested);
                break;
            case GTS_CMD_CAPTURE_POSITION:
            {
                GtsCapturePositionPacket* packet = new (std::nothrow) GtsCapturePositionPacket;
                if (!packet) { rc = -103; break; }
                ZeroMemory(packet, sizeof(*packet));
                packet->slot = request.captureSlot;
                packet->result = m_motion.CapturePlannedPositions(packet->positions);
                rc = packet->result;
                if (!::PostMessageW(m_hWnd, WM_GTS_CAPTURE_POS, 0,
                                    reinterpret_cast<LPARAM>(packet)))
                    delete packet;
                break;
            }
            case GTS_CMD_RESET_OUTPUTS:
                if (m_safetyTripped) rc = -116;
                else rc = m_motion.ResetMachineOutputs(request.extendLevelHigh,
                                                       request.resetExtend,
                                                       request.polarityConfirmed);
                break;
            case GTS_CMD_DISABLE:
                rc = m_motion.DisableAxes();
                break;
            case GTS_CMD_APPLY_SAFETY_POLARITY:
                rc = m_motion.ApplySafetyInputPolarity(request.lightCurtainActiveHigh,
                                                        request.stopInputActiveHigh);
                break;
            case GTS_CMD_READ_HOME_DIAGNOSTICS:
                rc = m_motion.PublishHomeDiagnostics();
                break;
            default:
                rc = -199;
                break;
            }
            if (request.command == GTS_CMD_HOME_AXIS ||
                request.command == GTS_CMD_HOME_SEQUENCE)
                m_motion.PublishHomeDiagnostics();
            m_motion.PublishAxisStatus();
            m_motion.PollIoStatus();
            m_extensionReady = m_motion.IsExtensionReady();
            m_uiInitialized = m_motion.IsInitialized();
        }
        ::PostMessageW(m_hWnd, WM_GTS_MOTION_DONE,
                       (WPARAM)request.command, (LPARAM)(LONG_PTR)rc);
    }
    m_motion.Close();
    return 0;
}

short CTrapDemoMFCDlg::RunDemoCommand(const GtsCommandRequest& request)
{
    auto checkStop = [this]() -> short
    {
        const bool curtain = InterlockedCompareExchange(&m_demoCurtain, 0, 0) != 0;
        const bool stop = InterlockedCompareExchange(&m_demoStop, 0, 0) != 0;
        if (curtain || stop)
        {
            m_safetyTripped = true;
            m_safetySource = (curtain ? GTS_SAFETY_LIGHT_CURTAIN : GTS_SAFETY_NONE) |
                             (stop ? GTS_SAFETY_SYSTEM_STOP : GTS_SAFETY_NONE);
            m_simOutputs &= ~((1L << 2));
            m_simOutputs |= (1L << 0) | (1L << 3);
            InterlockedExchange(&m_stopRequested, 1);
            m_motion.Log(curtain
                ? L"演示光幕触发：模拟停轴、绿灯关闭、红灯与蜂鸣器开启；气缸状态保持。"
                : L"演示系统停止触发：模拟停轴、绿灯关闭、红灯与蜂鸣器开启；气缸状态保持。");
            return -116;
        }
        return InterlockedCompareExchange(&m_stopRequested, 0, 0) != 0 ? -105 : 0;
    };
    auto setOutput = [this, &request](int output, bool on)
    {
        const int directIndex[] = { 0, 1, 2, 3, 7, 8, 9, 10 };
        if (output <= GTS_OUT_PRESS_CYLINDER)
        {
            int bit = directIndex[output];
            bool value = on;
            if (output == GTS_OUT_PRESS_CYLINDER)
                value = on ? request.extendLevelHigh[0] : !request.extendLevelHigh[0];
            if (value) m_simOutputs |= (1L << bit); else m_simOutputs &= ~(1L << bit);
        }
        else
        {
            int bit = output == GTS_OUT_RODLESS ? 0 : (output == GTS_OUT_BIN2 ? 1 : 2);
            int polarityIndex = output == GTS_OUT_RODLESS ? 1 : (output == GTS_OUT_BIN2 ? 2 : 3);
            bool value = on ? request.extendLevelHigh[polarityIndex] : !request.extendLevelHigh[polarityIndex];
            if (value) m_simExtOutputs |= (1u << bit); else m_simExtOutputs &= ~(1u << bit);
        }
    };
    auto delay = [this, &checkStop](DWORD duration) -> short
    {
        DWORD begin = GetTickCount();
        while (GetTickCount() - begin < duration)
        {
            short rc = checkStop(); if (rc != 0) return rc;
            Sleep(10);
        }
        return 0;
    };

    if (request.command == GTS_CMD_INIT)
    {
        m_simInitialized = true;
        m_simInputs = 0;
        m_safetyTripped = false;
        m_safetySource = GTS_SAFETY_NONE;
        // Preserve the simulated DI0 state selected on the IO page.
        m_extensionReady = true;
        m_uiInitialized = true;
        m_motion.Log(L"隔离演示模式已启动：未调用 GT_Open 或任何硬件 API。");
        return 0;
    }
    if (request.command == GTS_CMD_READ_HOME_DIAGNOSTICS)
    {
        m_motion.Log(L"隔离演示模式：HOME 参数、原始 DI 和限位状态均不读取真实硬件。");
        return 0;
    }
    if (request.command == GTS_CMD_ENABLE)
    {
        if (!m_simInitialized) return -101;
        for (int axis = 1; axis <= 3; ++axis) m_simEnabled[axis] = true;
        m_uiServoEnabled = true;
        m_motion.Log(L"演示模式：三轴伺服状态已模拟为使能。");
        return 0;
    }
    if (!m_simInitialized && request.command != GTS_CMD_NONE) return -101;

    if (request.command == GTS_CMD_DISABLE)
    {
        for (int axis = 1; axis <= 3; ++axis) m_simEnabled[axis] = false;
        m_uiServoEnabled = false;
        return 0;
    }
    if (request.command == GTS_CMD_CLEAR_ALARMS)
    {
        if (InterlockedCompareExchange(&m_demoCurtain, 0, 0) != 0 ||
            InterlockedCompareExchange(&m_demoStop, 0, 0) != 0) return -116;
        m_safetyTripped = false;
        m_safetySource = GTS_SAFETY_NONE;
        m_simOutputs &= ~((1L << 0) | (1L << 3));
        InterlockedExchange(&m_stopRequested, 0);
        m_motion.Log(L"演示模式：报警和软件联锁已清除。");
        return 0;
    }
    if (request.command == GTS_CMD_APPLY_SAFETY_POLARITY)
    {
        for (int axis = 1; axis <= 3; ++axis)
            if (m_simEnabled[axis]) return -117;
        m_lightCurtainActiveHigh = request.lightCurtainActiveHigh;
        m_stopInputActiveHigh = request.stopInputActiveHigh;
        m_motion.Log(L"演示模式：安全输入极性已模拟应用；联锁仍须显式清报警。");
        return 0;
    }
    if (request.command == GTS_CMD_IO_OUTPUT)
    {
        if (m_safetyTripped && request.outputOn) return -116;
        if (request.output >= GTS_OUT_PRESS_CYLINDER && !request.polarityConfirmed) return -131;
        setOutput(request.output, request.outputOn);
        return 0;
    }
    if (request.command == GTS_CMD_ZERO_AXIS)
    {
        if (request.axis < 1 || request.axis > 3) return -103;
        m_simPosition[request.axis] = 0;
        m_simHomed[request.axis] = false;
        return 0;
    }
    if (request.command == GTS_CMD_CAPTURE_POSITION)
    {
        GtsCapturePositionPacket* packet = new (std::nothrow) GtsCapturePositionPacket;
        if (!packet) return -103;
        ZeroMemory(packet, sizeof(*packet));
        packet->slot = request.captureSlot;
        packet->result = 0;
        for (int axis = 1; axis <= 3; ++axis) packet->positions[axis] = m_simPosition[axis];
        if (!::PostMessageW(m_hWnd, WM_GTS_CAPTURE_POS, 0, (LPARAM)packet)) delete packet;
        return 0;
    }
    if (request.command == GTS_CMD_MOVE_SINGLE || request.command == GTS_CMD_SEQUENCE ||
        request.command == GTS_CMD_JOG)
    {
        if (request.command == GTS_CMD_JOG)
        {
            const int axis = request.axis;
            if (axis < 1 || axis > 3 || !m_simEnabled[axis]) return -102;
            if (request.velocities[axis] <= 0.0 ||
                (request.direction != -1 && request.direction != 1)) return -103;
            m_motion.Log(request.direction > 0
                ? L"演示模式：正向 JOG 已启动，松开按钮停止。"
                : L"演示模式：负向 JOG 已启动，松开按钮停止。");
            DWORD begin = GetTickCount();
            DWORD lastPublish = begin;
            DWORD lastStep = begin;
            while (InterlockedCompareExchange(&m_stopRequested, 0, 0) == 0)
            {
                short rc = checkStop();
                if (rc != 0) return rc;
                const DWORD now = GetTickCount();
                if (now - begin >= 30000)
                {
                    m_motion.Log(L"演示 JOG 达到 30 秒看门狗上限，已自动停止。");
                    break;
                }
                if (now - lastStep >= 10)
                {
                    const double distance = request.velocities[axis] * (now - lastStep);
                    const long delta = max(1L, (long)(distance + 0.5));
                    m_simPosition[axis] += request.direction * delta;
                    lastStep = now;
                }
                if (now - lastPublish >= 200)
                {
                    PublishDemoStatus();
                    lastPublish = now;
                }
                Sleep(5);
            }
            m_motion.Log(L"演示模式：JOG 已停止。");
            return 0;
        }
        const int first = request.command == GTS_CMD_MOVE_SINGLE ? request.axis : 1;
        const int last = request.command == GTS_CMD_MOVE_SINGLE ? request.axis : 3;
        for (int axis = first; axis <= last; ++axis)
        {
            short rc = checkStop(); if (rc != 0) return rc;
            if (!m_simEnabled[axis]) return -102;
            m_simPosition[axis] = request.targets[axis];
            m_motion.Progress(axis, 3, request.command == GTS_CMD_SEQUENCE
                              ? L"演示模式：三轴依次运动" : L"演示模式：点位动作完成");
            rc = delay(180); if (rc != 0) return rc;
        }
        return 0;
    }
    if (request.command == GTS_CMD_HOME_AXIS || request.command == GTS_CMD_HOME_SEQUENCE)
    {
        const int count = request.command == GTS_CMD_HOME_AXIS ? 1 : 3;
        for (int i = 0; i < count; ++i)
        {
            const int axis = request.command == GTS_CMD_HOME_AXIS ? request.axis : kAxisOrder[i];
            short rc = checkStop(); if (rc != 0) return rc;
            if (!m_simEnabled[axis]) return -102;
            m_motion.Progress(i + 1, count, L"演示模式：执行 HOME 步骤");
            rc = delay(220); if (rc != 0) return rc;
            m_simPosition[axis] = 0;
            m_simHomed[axis] = true;
            m_axisHomed[axis] = true;
        }
        if (request.command == GTS_CMD_HOME_SEQUENCE && request.resetOutputs)
        {
            if (!request.polarityConfirmed) return -131;
            for (int output = 0; output < kOutputCount; ++output)
            {
                bool resetState = false;
                if (output == GTS_OUT_PRESS_CYLINDER) resetState = request.resetExtend[0];
                else if (output == GTS_OUT_RODLESS) resetState = request.resetExtend[1];
                else if (output == GTS_OUT_BIN2) resetState = request.resetExtend[2];
                else if (output == GTS_OUT_BIN3) resetState = request.resetExtend[3];
                setOutput(output, resetState);
            }
        }
        return 0;
    }
    if (request.command == GTS_CMD_RESET_OUTPUTS)
    {
        if (!request.polarityConfirmed) return -131;
        for (int output = 0; output < kOutputCount; ++output)
        {
            bool resetState = false;
            if (output == GTS_OUT_PRESS_CYLINDER) resetState = request.resetExtend[0];
            else if (output == GTS_OUT_RODLESS) resetState = request.resetExtend[1];
            else if (output == GTS_OUT_BIN2) resetState = request.resetExtend[2];
            else if (output == GTS_OUT_BIN3) resetState = request.resetExtend[3];
            setOutput(output, resetState);
        }
        return 0;
    }
    if (request.command == GTS_CMD_TRAJECTORY)
    {
        for (int axis = 1; axis <= 3; ++axis)
            if (!m_simEnabled[axis] || !m_simHomed[axis]) return -133;
        short rc = checkStop(); if (rc != 0) return rc;
        if (request.trajectory.kind == GTS_TRAJ_LINE)
        {
            m_simPosition[m_axisForXyz[0]] = request.trajectory.x;
            m_simPosition[m_axisForXyz[1]] = request.trajectory.y;
            m_simPosition[m_axisForXyz[2]] = request.trajectory.z;
        }
        else if (request.trajectory.kind == GTS_TRAJ_ARC)
        {
            m_simPosition[m_axisForXyz[0]] = request.trajectory.x;
            m_simPosition[m_axisForXyz[1]] = request.trajectory.y;
        }
        else
        {
            m_simPosition[m_axisForXyz[0]] = request.trajectory.centerX + request.trajectory.radius;
            m_simPosition[m_axisForXyz[1]] = request.trajectory.centerY;
        }
        m_motion.Progress(1, 1, L"演示模式：轨迹已模拟完成");
        return delay(350);
    }
    if (request.command == GTS_CMD_AUTO_PICK_PLACE)
    {
        if (!request.polarityConfirmed) return -131;
        for (int axis = 1; axis <= 3; ++axis)
            if (!m_simEnabled[axis] || !m_simHomed[axis]) return -133;
        for (int step = 1; step <= 9; ++step)
        {
            short rc = checkStop(); if (rc != 0) return rc;
            switch (step)
            {
            case 1: setOutput(GTS_OUT_GREEN, true); break;
            case 2: setOutput(GTS_OUT_RODLESS, true); break;
            case 3: setOutput(GTS_OUT_BIN2, true); break;
            case 4:
                for (int axis = 1; axis <= 3; ++axis) m_simPosition[axis] = request.recipe.pick[axis];
                setOutput(GTS_OUT_GRIPPER, true); setOutput(GTS_OUT_VACUUM, true); break;
            case 5:
                for (int axis = 1; axis <= 3; ++axis) m_simPosition[axis] = request.recipe.place[axis];
                setOutput(GTS_OUT_GRIPPER, false); setOutput(GTS_OUT_VACUUM, false); break;
            case 6: setOutput(GTS_OUT_BIN2, request.resetExtend[2]); break;
            case 7:
            {
                const bool resetRodlessExtended = request.resetExtend[1];
                setOutput(GTS_OUT_RODLESS, resetRodlessExtended);
                const LONG bitMask = resetRodlessExtended ? 0x0001 : 0x0002;
                const bool activeHigh = resetRodlessExtended
                    ? request.rodlessInPositionActiveHigh
                    : request.rodlessHomeActiveHigh;
                LONG observed = 0;
                LONG desired = 0;
                do
                {
                    observed = InterlockedCompareExchange(&m_simExtInputs, 0, 0);
                    desired = activeHigh ? (observed | bitMask) : (observed & ~bitMask);
                } while (InterlockedCompareExchange(&m_simExtInputs, desired, observed) != observed);
                break;
            }
            case 8:
                for (int axis = 1; axis <= 3; ++axis) m_simPosition[axis] = request.recipe.safe[axis];
                break;
            case 9: setOutput(GTS_OUT_GREEN, false); break;
            }
            m_motion.Progress(step, 9, L"演示模式：抓放步骤已模拟");
            if (step == 2 || step == 7)
            {
                const DWORD begin = GetTickCount();
                const bool returningToHome = step == 7 && !request.resetExtend[1];
                const unsigned short targetBit = step == 2 || !returningToHome ? 0x0001 : 0x0002;
                const bool activeHigh = targetBit == 0x0001
                    ? request.rodlessInPositionActiveHigh
                    : request.rodlessHomeActiveHigh;
                for (;;)
                {
                    rc = checkStop(); if (rc != 0) return rc;
                    const bool inputActive =
                        ((InterlockedCompareExchange(&m_simExtInputs, 0, 0) & targetBit) != 0) == activeHigh;
                    if (inputActive) break;
                    if (GetTickCount() - begin >= request.rodlessTimeoutMs)
                    {
                        m_motion.Log(targetBit == 0x0001
                            ? L"演示 DI0 未在设定时间内到位；自动抓放后续步骤已取消。"
                            : L"演示 DI1 未在设定时间内到位；自动抓放后续步骤已取消。");
                        return -134;
                    }
                    Sleep(20);
                }
            }
            else
            {
                rc = delay(100); if (rc != 0) return rc;
            }
        }
        return 0;
    }
    return -199;
}

void CTrapDemoMFCDlg::PublishDemoStatus()
{
    if (!m_simInitialized || !m_hWnd) return;
    GtsAxisStatusPacket* packet = new (std::nothrow) GtsAxisStatusPacket;
    if (!packet) return;
    ZeroMemory(packet, sizeof(*packet));
    packet->initialized = true; packet->opened = true; packet->extensionReady = true;
    for (int axis = 1; axis <= 3; ++axis)
    {
        packet->axisEnabled[axis - 1] = m_simEnabled[axis];
        packet->rows[axis - 1].statusRc = 0;
        packet->rows[axis - 1].prfRc = 0;
        packet->rows[axis - 1].prfPos = (double)m_simPosition[axis];
        packet->rows[axis - 1].status = (m_simEnabled[axis] ? 0x0200 : 0) |
                                       (m_safetyTripped ? 0x0100 : 0);
    }
    if (!::PostMessageW(m_hWnd, WM_GTS_AXIS_STATUS, 0, (LPARAM)packet)) delete packet;
}

void CTrapDemoMFCDlg::PublishDemoIo()
{
    if (!m_simInitialized || !m_hWnd) return;
    GtsIoStatusPacket* packet = new (std::nothrow) GtsIoStatusPacket;
    if (!packet) return;
    ZeroMemory(packet, sizeof(*packet));
    packet->extensionReady = true;
    packet->directInputs = m_simInputs;
    const bool curtainActive = InterlockedCompareExchange(&m_demoCurtain, 0, 0) != 0;
    const bool stopActive = InterlockedCompareExchange(&m_demoStop, 0, 0) != 0;
    if (curtainActive || stopActive)
    {
        m_safetyTripped = true;
        m_safetySource = (curtainActive ? GTS_SAFETY_LIGHT_CURTAIN : GTS_SAFETY_NONE) |
                         (stopActive ? GTS_SAFETY_SYSTEM_STOP : GTS_SAFETY_NONE);
        m_simOutputs &= ~(1L << 2);
        m_simOutputs |= (1L << 0) | (1L << 3);
    }
    packet->directInputs &= ~((1L << 1) | (1L << 4));
    packet->lightCurtainRaw = curtainActive == m_lightCurtainActiveHigh;
    packet->stopInputRaw = stopActive == m_stopInputActiveHigh;
    if (packet->lightCurtainRaw) packet->directInputs |= (1L << 4);
    if (packet->stopInputRaw) packet->directInputs |= (1L << 1);
    packet->lightCurtainActive = curtainActive;
    packet->stopInputActive = stopActive;
    packet->safetyActive = curtainActive || stopActive || m_safetyTripped;
    packet->safetySource = (curtainActive ? GTS_SAFETY_LIGHT_CURTAIN : GTS_SAFETY_NONE) |
                           (stopActive ? GTS_SAFETY_SYSTEM_STOP : GTS_SAFETY_NONE);
    if (packet->safetySource == GTS_SAFETY_NONE && m_safetyTripped)
        packet->safetySource = m_safetySource;
    packet->directOutputs = m_simOutputs;
    packet->extensionInputs = (unsigned short)InterlockedCompareExchange(&m_simExtInputs, 0, 0);
    packet->extensionOutputs = m_simExtOutputs;
    packet->directInputRc = packet->directOutputRc = 0;
    packet->extensionInputRc = packet->extensionOutputRc = 0;
    if (!::PostMessageW(m_hWnd, WM_GTS_IO_STATUS, 0, (LPARAM)packet)) delete packet;
}

void CTrapDemoMFCDlg::AppendLogUi(const wchar_t* text)
{
    if (!text || !m_logEdit.GetSafeHwnd()) return;
    const bool autoScroll = IsDlgButtonChecked(IDC_CHECK_LOG_AUTOSCROLL) == BST_CHECKED;
    const int firstVisible = m_logEdit.GetFirstVisibleLine();
    SYSTEMTIME st; GetLocalTime(&st);
    CString line;
    line.Format(_T("[%02u:%02u:%02u.%03u] %s\r\n"), st.wHour, st.wMinute,
                st.wSecond, st.wMilliseconds, text);
    const int length = m_logEdit.GetWindowTextLength();
    m_logEdit.SetSel(length, length);
    m_logEdit.ReplaceSel(line);
    if (autoScroll)
    {
        m_logEdit.SetSel(-1, -1);
        m_logEdit.SendMessage(EM_SCROLLCARET, 0, 0);
    }
    else
    {
        const int nowFirst = m_logEdit.GetFirstVisibleLine();
        m_logEdit.LineScroll(firstVisible - nowFirst);
    }
}

void CTrapDemoMFCDlg::ClearLogUi()
{
    if (m_logEdit.GetSafeHwnd()) m_logEdit.SetWindowText(_T(""));
}

void CTrapDemoMFCDlg::UpdateIoLabels(const GtsIoStatusPacket& packet)
{
    const int directOutputBits[kOutputCount] = { 0, 1, 2, 3, 7, 8, 9, 10, -1, -1, -1 };
    for (int output = 0; output < kOutputCount && output < (int)m_outputStatusIds.size(); ++output)
    {
        CString text;
        bool known = false, on = false;
        if (output <= GTS_OUT_PRESS_CYLINDER && packet.directOutputRc == 0)
        {
            known = true;
            on = (packet.directOutputs & (1L << directOutputBits[output])) != 0;
        }
        else if (output >= GTS_OUT_RODLESS && packet.extensionOutputRc == 0)
        {
            known = true;
            const int bit = output == GTS_OUT_RODLESS ? 0 : (output == GTS_OUT_BIN2 ? 1 : 2);
            on = (packet.extensionOutputs & (1u << bit)) != 0;
        }
        if (known) text.Format(_T("输出：%s"), on ? _T("开") : _T("关"));
        else text = packet.extensionReady || output <= GTS_OUT_PRESS_CYLINDER
                    ? _T("读取失败") : _T("模块未连接");
        SetDlgItemText(m_outputStatusIds[output], text);
    }
    for (size_t i = 0; i < m_inputBitNumbers.size(); ++i)
    {
        CString value;
        if (packet.directInputRc != 0) value = _T("读取失败");
        else value = (packet.directInputs & (1L << m_inputBitNumbers[i])) ? _T("有效") : _T("无效");
        if (i < m_inputStatusIds.size()) SetDlgItemText(m_inputStatusIds[i], value);
    }
    for (size_t i = 0; i < m_extInputBitNumbers.size(); ++i)
    {
        CString value;
        if (!packet.extensionReady) value = _T("未连接");
        else if (packet.extensionInputRc != 0) value = _T("读取失败");
        else value = (packet.extensionInputs & (1u << m_extInputBitNumbers[i])) ? _T("有效") : _T("无效");
        if (i < m_extInputStatusIds.size()) SetDlgItemText(m_extInputStatusIds[i], value);
    }
    CString stopText, curtainText;
    if (packet.directInputRc != 0)
    {
        stopText = _T("EXI1 系统停止：读取失败");
        curtainText = _T("EXI4 光幕：读取失败");
    }
    else
    {
        stopText.Format(_T("EXI1 系统停止：原始 %s；%s有效；%s"),
            packet.stopInputRaw ? _T("高") : _T("低"),
            m_stopInputActiveHigh ? _T("高电平") : _T("低电平"),
            packet.stopInputActive ? _T("已触发") : _T("未触发"));
        curtainText.Format(_T("EXI4 光幕：原始 %s；%s有效；%s"),
            packet.lightCurtainRaw ? _T("高") : _T("低"),
            m_lightCurtainActiveHigh ? _T("高电平") : _T("低电平"),
            packet.lightCurtainActive ? _T("已触发") : _T("未触发"));
    }
    SetDlgItemText(IDC_STATIC_EXI1_DIAG, stopText);
    SetDlgItemText(IDC_STATIC_EXI4_DIAG, curtainText);
}

void CTrapDemoMFCDlg::UpdateUiState()
{
    const bool busy = InterlockedCompareExchange(&m_busy, 0, 0) != 0;
    const bool safeChecked = OperatorConfirmed();
    const bool safetyReady = m_safetyInputsValid && !m_safetyTripped;
    const bool canRun = !busy && m_uiInitialized && m_uiServoEnabled && safeChecked && safetyReady;
    const bool demo = m_demoMode;
    const short selectedAxis = SelectedAxis();
    const bool selectedHomeConfirmed =
        selectedAxis >= 1 && selectedAxis <= 3 && m_homeConfirmed[selectedAxis];
    const bool allHomeConfirmed = m_homeConfirmed[1] && m_homeConfirmed[2] &&
                                  m_homeConfirmed[3];
    if (GetDlgItem(IDC_BTN_INIT)) GetDlgItem(IDC_BTN_INIT)->EnableWindow(!busy && !m_uiInitialized);
    if (GetDlgItem(IDC_BTN_ENABLE)) GetDlgItem(IDC_BTN_ENABLE)->EnableWindow(!busy && m_uiInitialized && !m_uiServoEnabled && safeChecked && safetyReady);
    if (GetDlgItem(IDC_BTN_DISABLE)) GetDlgItem(IDC_BTN_DISABLE)->EnableWindow(!busy && m_uiInitialized && m_uiServoEnabled);
    if (GetDlgItem(IDC_BTN_STOP)) GetDlgItem(IDC_BTN_STOP)->EnableWindow(busy);
    if (GetDlgItem(IDC_BTN_STOP_AUTO_PAGE)) GetDlgItem(IDC_BTN_STOP_AUTO_PAGE)->EnableWindow(busy);
    if (GetDlgItem(IDC_BTN_MOVE)) GetDlgItem(IDC_BTN_MOVE)->EnableWindow(canRun);
    if (GetDlgItem(IDC_BTN_SEQUENCE)) GetDlgItem(IDC_BTN_SEQUENCE)->EnableWindow(canRun);
    if (GetDlgItem(IDC_BTN_JOG_NEG)) GetDlgItem(IDC_BTN_JOG_NEG)->EnableWindow(canRun || InterlockedCompareExchange(&m_activeCommand, 0, 0) == GTS_CMD_JOG);
    if (GetDlgItem(IDC_BTN_JOG_POS)) GetDlgItem(IDC_BTN_JOG_POS)->EnableWindow(canRun || InterlockedCompareExchange(&m_activeCommand, 0, 0) == GTS_CMD_JOG);
    if (GetDlgItem(IDC_BTN_HOME)) GetDlgItem(IDC_BTN_HOME)->EnableWindow(canRun && (demo || selectedHomeConfirmed));
    if (GetDlgItem(IDC_BTN_HOME_SEQUENCE)) GetDlgItem(IDC_BTN_HOME_SEQUENCE)->EnableWindow(canRun && (demo || allHomeConfirmed));
    if (GetDlgItem(IDC_BTN_HOME_SEQUENCE_MANUAL)) GetDlgItem(IDC_BTN_HOME_SEQUENCE_MANUAL)->EnableWindow(canRun && (demo || allHomeConfirmed));
    if (GetDlgItem(IDC_BTN_HOME_RESET)) GetDlgItem(IDC_BTN_HOME_RESET)->EnableWindow(canRun && (demo || allHomeConfirmed) && m_polarityConfirmed && m_extensionReady);
    if (GetDlgItem(IDC_BTN_HOME_RESET_MANUAL)) GetDlgItem(IDC_BTN_HOME_RESET_MANUAL)->EnableWindow(canRun && (demo || allHomeConfirmed) && m_polarityConfirmed && m_extensionReady);
    if (GetDlgItem(IDC_BTN_HOME_DIAG)) GetDlgItem(IDC_BTN_HOME_DIAG)->EnableWindow(!busy && m_uiInitialized);
    for (int axis = 1; axis <= 3; ++axis)
    {
        const int id = IDC_CHECK_HOME_CONFIRMED_1 + axis - 1;
        if (GetDlgItem(id))
            GetDlgItem(id)->EnableWindow(!demo && !busy && m_uiInitialized &&
                                          m_homeDiagnosticsReceived[axis]);
    }
    if (GetDlgItem(IDC_BTN_CLEAR_ALARMS)) GetDlgItem(IDC_BTN_CLEAR_ALARMS)->EnableWindow(!busy && m_uiInitialized);
    if (GetDlgItem(IDC_BTN_CLEAR_ALARMS_SETTINGS)) GetDlgItem(IDC_BTN_CLEAR_ALARMS_SETTINGS)->EnableWindow(!busy && m_uiInitialized);
    if (GetDlgItem(IDC_BTN_ZERO_AXIS)) GetDlgItem(IDC_BTN_ZERO_AXIS)->EnableWindow(!busy && m_uiInitialized);
    if (GetDlgItem(IDC_BTN_ZERO_AXIS_SETTINGS)) GetDlgItem(IDC_BTN_ZERO_AXIS_SETTINGS)->EnableWindow(!busy && m_uiInitialized);
    if (GetDlgItem(IDC_BTN_START_AUTO)) GetDlgItem(IDC_BTN_START_AUTO)->EnableWindow(canRun && m_extensionReady && m_polarityConfirmed && m_taught[GTS_CAPTURE_PICK] && m_taught[GTS_CAPTURE_PLACE] && m_taught[GTS_CAPTURE_SAFE]);
    if (GetDlgItem(IDC_BTN_AUTO_START_PAGE)) GetDlgItem(IDC_BTN_AUTO_START_PAGE)->EnableWindow(canRun && m_extensionReady && m_polarityConfirmed && m_taught[GTS_CAPTURE_PICK] && m_taught[GTS_CAPTURE_PLACE] && m_taught[GTS_CAPTURE_SAFE]);
    if (GetDlgItem(IDC_BTN_RESET_OUTPUTS_PAGE)) GetDlgItem(IDC_BTN_RESET_OUTPUTS_PAGE)->EnableWindow(!busy && m_uiInitialized && m_extensionReady && m_polarityConfirmed && !m_safetyTripped);
    if (GetDlgItem(IDC_BTN_IO_REFRESH)) GetDlgItem(IDC_BTN_IO_REFRESH)->EnableWindow(!busy && m_uiInitialized);
    if (GetDlgItem(IDC_BTN_IO_REFRESH_PAGE)) GetDlgItem(IDC_BTN_IO_REFRESH_PAGE)->EnableWindow(!busy && m_uiInitialized);
    if (GetDlgItem(IDC_COMBO_MODE)) GetDlgItem(IDC_COMBO_MODE)->EnableWindow(!busy && !m_uiInitialized);
    if (GetDlgItem(IDC_CHECK_DEMO_RODLESS)) GetDlgItem(IDC_CHECK_DEMO_RODLESS)->EnableWindow(demo);
    if (GetDlgItem(IDC_CHECK_DEMO_CURTAIN)) GetDlgItem(IDC_CHECK_DEMO_CURTAIN)->EnableWindow(demo);
    if (GetDlgItem(IDC_CHECK_DEMO_CURTAIN_SETTINGS)) GetDlgItem(IDC_CHECK_DEMO_CURTAIN_SETTINGS)->EnableWindow(demo);
    if (GetDlgItem(IDC_CHECK_DEMO_STOP)) GetDlgItem(IDC_CHECK_DEMO_STOP)->EnableWindow(demo);
    if (GetDlgItem(IDC_CHECK_DEMO_STOP_SETTINGS)) GetDlgItem(IDC_CHECK_DEMO_STOP_SETTINGS)->EnableWindow(demo);
    if (GetDlgItem(IDC_CHECK_LIGHT_ACTIVE)) GetDlgItem(IDC_CHECK_LIGHT_ACTIVE)->EnableWindow(!busy && !m_uiServoEnabled);
    if (GetDlgItem(IDC_CHECK_STOP_ACTIVE)) GetDlgItem(IDC_CHECK_STOP_ACTIVE)->EnableWindow(!busy && !m_uiServoEnabled);
    if (GetDlgItem(IDC_BTN_APPLY_SAFETY_POLARITY))
        GetDlgItem(IDC_BTN_APPLY_SAFETY_POLARITY)->EnableWindow(!busy && !m_uiServoEnabled);
    for (int i = 0; i < kOutputCount; ++i)
    {
        HWND on = FindControlHwnd(IDC_IO_ON_BASE + i);
        HWND off = FindControlHwnd(IDC_IO_OFF_BASE + i);
        const bool extAvailable = i < GTS_OUT_RODLESS || m_extensionReady;
        const bool cylinderConfigConfirmed = i < GTS_OUT_PRESS_CYLINDER || m_polarityConfirmed;
        if (on) ::EnableWindow(on, !busy && m_uiInitialized && safeChecked && !m_safetyTripped && extAvailable && cylinderConfigConfirmed);
        if (off) ::EnableWindow(off, !busy && m_uiInitialized && !m_safetyTripped && extAvailable && cylinderConfigConfirmed);
    }

    CString controller;
    if (demo && m_uiInitialized) controller = _T("演示：状态由隔离模拟器生成");
    else if (demo) controller = _T("演示：尚未启动");
    else if (!m_uiInitialized) controller = _T("控制器：未初始化");
    else if (busy) controller = _T("控制器：任务执行中");
    else if (m_uiServoEnabled) controller = _T("控制器：已初始化，伺服已使能");
    else controller = _T("控制器：已初始化，伺服关闭");
    SetDlgItemText(m_controllerStatusId, controller);
    SetDlgItemText(m_extensionStatusId, m_extensionReady ? _T("gLink200：已连接") : (demo && m_uiInitialized ? _T("gLink200：演示状态") : _T("gLink200：未连接")));
    SetDlgItemText(m_feedbackStatusId, _T("位置反馈：开环，无编码器"));
    CString safetyText;
    if (!m_safetyInputsValid)
        safetyText = _T("安全锁止：EXI1/EXI4 输入未确认或读取失败");
    else if (m_safetyTripped)
    {
        if ((m_safetySource & GTS_SAFETY_SYSTEM_STOP) && (m_safetySource & GTS_SAFETY_LIGHT_CURTAIN))
            safetyText = _T("安全锁止：EXI1 系统停止 + EXI4 光幕");
        else if (m_safetySource & GTS_SAFETY_SYSTEM_STOP)
            safetyText = _T("安全锁止：EXI1 系统停止");
        else if (m_safetySource & GTS_SAFETY_LIGHT_CURTAIN)
            safetyText = _T("安全锁止：EXI4 光幕");
        else safetyText = _T("安全锁止：等待安全输入复位");
    }
    else safetyText = _T("安全状态：须以实物输入和硬件回路为准");
    SetDlgItemText(m_hardwareStatusId, safetyText);
}

LRESULT CTrapDemoMFCDlg::OnMotionLog(WPARAM, LPARAM lParam)
{
    wchar_t* text = reinterpret_cast<wchar_t*>(lParam);
    if (text) { AppendLogUi(text); delete[] text; }
    return 0;
}

LRESULT CTrapDemoMFCDlg::OnMotionDone(WPARAM wParam, LPARAM lParam)
{
    const LONG command = (LONG)wParam;
    const short rc = (short)(LONG_PTR)lParam;
    InterlockedExchange(&m_busy, 0);
    InterlockedExchange(&m_activeCommand, GTS_CMD_NONE);
    InterlockedExchange(&m_activeJogDirection, 0);
    if (command == GTS_CMD_INIT && rc == 0) m_uiInitialized = true;
    if (command == GTS_CMD_ENABLE && rc == 0) m_uiServoEnabled = true;
    if (command == GTS_CMD_DISABLE && rc == 0) m_uiServoEnabled = false;
    if (command == GTS_CMD_CLEAR_ALARMS && rc == 0)
    {
        m_safetyTripped = false;
        m_safetySource = GTS_SAFETY_NONE;
        InterlockedExchange(&m_stopRequested, 0);
        AppendLogUi(L"显式清报警成功：工作线程已确认 EXI1/EXI4 均未触发，软件联锁已解除。");
    }
    if (command == GTS_CMD_APPLY_SAFETY_POLARITY)
    {
        if (rc == 0)
        {
            m_lightCurtainActiveHigh = m_pendingLightCurtainActiveHigh;
            m_stopInputActiveHigh = m_pendingStopInputActiveHigh;
            CheckDlgButton(IDC_CHECK_LIGHT_ACTIVE, m_lightCurtainActiveHigh ? BST_CHECKED : BST_UNCHECKED);
            CheckDlgButton(IDC_CHECK_STOP_ACTIVE, m_stopInputActiveHigh ? BST_CHECKED : BST_UNCHECKED);
            SaveSettings();
            AppendLogUi(L"安全输入极性已由后台任务应用；联锁状态未被自动清除。请重新读取 EXI1/EXI4，再显式清报警。");
        }
        else
        {
            CheckDlgButton(IDC_CHECK_LIGHT_ACTIVE, m_lightCurtainActiveHigh ? BST_CHECKED : BST_UNCHECKED);
            CheckDlgButton(IDC_CHECK_STOP_ACTIVE, m_stopInputActiveHigh ? BST_CHECKED : BST_UNCHECKED);
            AppendLogUi(L"安全输入极性未能应用；请确认伺服关闭、轴静止后重试。");
        }
    }
    if (command == GTS_CMD_HOME_AXIS && rc == 0) m_axisHomed[m_lastCommandAxis] = true;
    if (command == GTS_CMD_HOME_SEQUENCE && rc == 0)
        for (int i = 1; i <= 3; ++i) m_axisHomed[i] = true;
    if (command == GTS_CMD_ZERO_AXIS && rc == 0) m_axisHomed[m_lastCommandAxis] = false;
    if (command == GTS_CMD_INIT && !m_demoMode) m_extensionReady = m_motion.IsExtensionReady();
    if (command == GTS_CMD_INIT && m_demoMode) m_extensionReady = true;
    if (command == GTS_CMD_INIT && m_demoMode)
        SetDlgItemText(IDC_STATIC_HOME_RAW,
                       _T("隔离演示模式：不读取真实控制器 HOME 参数、DI 或限位状态。"));
    if (command == GTS_CMD_HOME_AXIS && rc != 0 && m_lastCommandAxis >= 1 &&
        m_lastCommandAxis <= 3)
    {
        m_axisHomed[m_lastCommandAxis] = false;
        m_homeConfirmed[m_lastCommandAxis] = false;
        ZeroMemory(&m_homeConfirmedSettings[m_lastCommandAxis],
                   sizeof(m_homeConfirmedSettings[m_lastCommandAxis]));
        CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + m_lastCommandAxis - 1, BST_UNCHECKED);
        AppendLogUi(L"单轴 HOME 未成功，已撤销该轴现场确认；重新核对状态后再试。");
    }
    if (command == GTS_CMD_HOME_SEQUENCE && rc != 0 && !m_demoMode)
    {
        for (int axis = 1; axis <= 3; ++axis)
        {
            m_homeConfirmed[axis] = false;
            ZeroMemory(&m_homeConfirmedSettings[axis], sizeof(m_homeConfirmedSettings[axis]));
            CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + axis - 1, BST_UNCHECKED);
        }
        AppendLogUi(L"三轴 HOME 序列未成功，已撤销全部轴的现场确认；后续轴未启动。");
    }
    CString progress;
    if (rc == 0) progress = _T("当前任务：完成");
    else progress.Format(_T("当前任务：结束，返回码 %d"), (int)rc);
    SetDlgItemText(m_progressLabelId, progress);
    wchar_t message[220] = {};
    _snwprintf_s(message, _countof(message), _TRUNCATE,
                 L"任务结束：命令=%ld，返回值=%d。", command, (int)rc);
    AppendLogUi(message);
    if (rc == -130) AppendLogUi(L"gLink200 不可用：请检查扩展模块、地址 0 和 ExtMdl.cfg。");
    if (rc == -131) AppendLogUi(L"气缸输出极性尚未确认，已阻止复位/自动抓放动作。");
    if (rc == -134) AppendLogUi(L"无杆气缸目标端位 DI0/DI1 未在超时前到位，流程未继续。");
    if (rc == 8) AppendLogUi(L"HOME 搜索未捕获原点；检查 HOME 传感器接线、映射、有效电平和方向。");
    if (rc == -114 || rc == -115)
        AppendLogUi(L"HOME 搜索方向上的限位已触发，控制器请求停止且后续轴已取消；请核对搜索方向和限位状态。");
    if (rc == -110 || rc == -111)
        AppendLogUi(L"HOME 期间检测到驱动报警或急停状态，后续轴已取消。");
    UpdateUiState();
    return 0;
}

LRESULT CTrapDemoMFCDlg::OnJogButtonDown(WPARAM wParam, LPARAM)
{
    const int direction = (int)(INT_PTR)wParam;
    if (!m_uiInitialized || !m_uiServoEnabled || !OperatorConfirmed() || m_safetyTripped)
    {
        AppendLogUi(L"JOG 未启动：先初始化、使能并确认安全条件；安全联锁触发时需先复位。");
        return 0;
    }
    double speed = 0.0, acc = 0.0, dec = 0.0;
    if (!ReadPositiveDouble(IDC_EDIT_JOG_SPEED_NEW, speed) ||
        !ReadPositiveDouble(IDC_EDIT_JOG_ACC_NEW, acc, 100000.0) ||
        !ReadPositiveDouble(IDC_EDIT_JOG_DEC_NEW, dec, 100000.0))
    {
        AppendLogUi(L"JOG 参数无效。");
        return 0;
    }
    GtsCommandRequest request = DefaultRequest(GTS_CMD_JOG);
    request.axis = SelectedAxis(); request.direction = direction;
    request.velocities[request.axis] = speed;
    request.acceleration = acc; request.deceleration = dec;
    SubmitRequest(request);
    return 0;
}

LRESULT CTrapDemoMFCDlg::OnJogButtonUp(WPARAM wParam, LPARAM)
{
    const int direction = (int)(INT_PTR)wParam;
    if (InterlockedCompareExchange(&m_activeCommand, 0, 0) == GTS_CMD_JOG &&
        InterlockedCompareExchange(&m_activeJogDirection, 0, 0) == direction)
        InterlockedExchange(&m_stopRequested, 1);
    return 0;
}

LRESULT CTrapDemoMFCDlg::OnAxisStatus(WPARAM, LPARAM lParam)
{
    GtsAxisStatusPacket* packet = reinterpret_cast<GtsAxisStatusPacket*>(lParam);
    if (!packet) return 0;
    bool readError = false, warning = false, anyServo = false;
    for (int i = 0; i < 3; ++i)
    {
        const GtsAxisStatusRow& row = packet->rows[i];
        if (row.statusRc != 0)
        {
            readError = true;
            for (int col = 1; col < 7; ++col) m_axisStatusList.SetItemText(i, col, _T("读取失败"));
            continue;
        }
        const long sts = row.status;
        const bool alarm = (sts & 0x0002) != 0;
        const bool posLimit = (sts & 0x0020) != 0;
        const bool negLimit = (sts & 0x0040) != 0;
        const bool stopIo = (sts & 0x0080) != 0;
        const bool estopIo = (sts & 0x0100) != 0;
        const bool servo = (sts & 0x0200) != 0;
        const bool moving = (sts & 0x0400) != 0;
        anyServo = anyServo || servo;
        warning = warning || alarm || posLimit || negLimit || stopIo || estopIo;
        m_axisStatusList.SetItemText(i, 1, servo ? _T("已使能") : _T("已关闭"));
        m_axisStatusList.SetItemText(i, 2, moving ? _T("运动中") : _T("停止"));
        m_axisStatusList.SetItemText(i, 3, posLimit ? _T("触发") : _T("正常"));
        m_axisStatusList.SetItemText(i, 4, negLimit ? _T("触发") : _T("正常"));
        m_axisStatusList.SetItemText(i, 5, alarm ? _T("报警") : _T("正常"));
        CString pos;
        if (row.prfRc == 0) pos.Format(_T("%.1f  (无编码器)"), row.prfPos);
        else pos = _T("读取失败");
        m_axisStatusList.SetItemText(i, 6, pos);
    }
    if (!readError && packet->initialized) m_uiServoEnabled = anyServo;
    m_extensionReady = packet->extensionReady || m_demoMode;
    if (readError) SetDlgItemText(m_hardwareStatusId, _T("状态监视：读取失败，请检查控制器通信"));
    else if (warning) SetDlgItemText(m_hardwareStatusId, _T("状态监视：轴报警/限位/停止标志需处理"));
    else if (!m_safetyTripped) SetDlgItemText(m_hardwareStatusId, _T("状态监视：轴状态正常；仍须核实实体安全回路"));
    delete packet;
    UpdateUiState();
    return 0;
}

LRESULT CTrapDemoMFCDlg::OnIoStatus(WPARAM, LPARAM lParam)
{
    GtsIoStatusPacket* packet = reinterpret_cast<GtsIoStatusPacket*>(lParam);
    if (!packet) return 0;
    m_extensionReady = packet->extensionReady || m_demoMode;
    if (packet->safetyActive)
    {
        m_safetyTripped = true;
        if (packet->safetySource != GTS_SAFETY_NONE) m_safetySource = packet->safetySource;
        if (InterlockedCompareExchange(&m_busy, 0, 0) != 0)
            InterlockedExchange(&m_stopRequested, 1);
    }
    m_safetyInputsValid = packet->directInputRc == 0;
    if (!m_safetyInputsValid)
    {
        const bool wasTripped = m_safetyTripped;
        m_safetyTripped = true;
        m_safetySource = GTS_SAFETY_NONE;
        if (!wasTripped) AppendLogUi(L"EXI1/EXI4 输入读取失败，已锁止新动作；恢复通信并确认输入安全后显式清报警。");
        if (InterlockedCompareExchange(&m_busy, 0, 0) != 0)
            InterlockedExchange(&m_stopRequested, 1);
    }
    UpdateIoLabels(*packet);
    delete packet;
    UpdateUiState();
    return 0;
}

LRESULT CTrapDemoMFCDlg::OnProgress(WPARAM, LPARAM lParam)
{
    GtsProgressPacket* packet = reinterpret_cast<GtsProgressPacket*>(lParam);
    if (!packet) return 0;
    CString text;
    text.Format(_T("当前任务：%d/%d  %s"), packet->step, packet->total, packet->text);
    SetDlgItemText(m_progressLabelId, text);
    AppendLogUi(packet->text);
    delete packet;
    return 0;
}

void CTrapDemoMFCDlg::UpdateCaptureState(const GtsCapturePositionPacket& packet)
{
    if (packet.result != 0 || packet.slot < GTS_CAPTURE_PICK || packet.slot > GTS_CAPTURE_SAFE)
    {
        AppendLogUi(L"示教读取规划位置失败。");
        return;
    }
    for (int axis = 1; axis <= 3; ++axis) m_taughtPositions[packet.slot][axis] = packet.positions[axis];
    m_taught[packet.slot] = true;
    CString text;
    const int labelIds[] = { 0, IDC_STATIC_CAPTURE_PICK, IDC_STATIC_CAPTURE_PLACE, IDC_STATIC_CAPTURE_SAFE };
    const wchar_t* names[] = { L"", L"抓取位", L"放置位", L"安全零位" };
    text.Format(_T("%s：X=%ld  Y=%ld  Z=%ld pulse"), names[packet.slot],
                packet.positions[1], packet.positions[2], packet.positions[3]);
    SetDlgItemText(labelIds[packet.slot], text);
    AppendLogUi(text);
    SaveSettings();
    UpdateUiState();
}

LRESULT CTrapDemoMFCDlg::OnCapturePosition(WPARAM, LPARAM lParam)
{
    GtsCapturePositionPacket* packet = reinterpret_cast<GtsCapturePositionPacket*>(lParam);
    if (packet) { UpdateCaptureState(*packet); delete packet; }
    return 0;
}

BOOL CTrapDemoMFCDlg::OnCommand(WPARAM wParam, LPARAM lParam)
{
    const int id = LOWORD(wParam);
    const int code = HIWORD(wParam);
    if (code == CBN_SELCHANGE)
    {
        const int triggerIds[] = { IDC_COMBO_HOME_TRIGGER_1, IDC_COMBO_HOME_TRIGGER_2, IDC_COMBO_HOME_TRIGGER_3 };
        const int edgeIds[] = { IDC_COMBO_HOME_EDGE_1, IDC_COMBO_HOME_EDGE_2, IDC_COMBO_HOME_EDGE_3 };
        for (int i = 0; i < 3; ++i)
        {
            if (id != triggerIds[i] && id != edgeIds[i]) continue;
            m_homeConfirmed[i + 1] = false;
            CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + i, BST_UNCHECKED);
            const int triggerSelection = (int)::SendMessageW(
                FindControlHwnd(triggerIds[i]), CB_GETCURSEL, 0, 0);
            const int edgeSelection = (int)::SendMessageW(
                FindControlHwnd(edgeIds[i]), CB_GETCURSEL, 0, 0);
            m_homeSettings[i + 1].overrideTriggerIndex = triggerSelection == 1;
            m_homeSettings[i + 1].triggerIndex = -1;
            m_homeSettings[i + 1].overrideEdge = edgeSelection > 0;
            m_homeSettings[i + 1].edge = edgeSelection > 0 ? (short)(edgeSelection - 1) : 0;
            SaveSettings();
            UpdateUiState();
            return TRUE;
        }
    }
    if (code == EN_CHANGE)
    {
        const int dirIds[] = { IDC_EDIT_HOME_DIR1, IDC_EDIT_HOME_DIR2, IDC_EDIT_HOME_DIR3 };
        const int highIds[] = { IDC_EDIT_HOME_HIGH1, IDC_EDIT_HOME_HIGH2, IDC_EDIT_HOME_HIGH3 };
        const int lowIds[] = { IDC_EDIT_HOME_LOW1, IDC_EDIT_HOME_LOW2, IDC_EDIT_HOME_LOW3 };
        const int accIds[] = { IDC_EDIT_HOME_ACC1, IDC_EDIT_HOME_ACC2, IDC_EDIT_HOME_ACC3 };
        const int decIds[] = { IDC_EDIT_HOME_DEC1, IDC_EDIT_HOME_DEC2, IDC_EDIT_HOME_DEC3 };
        const int distIds[] = { IDC_EDIT_HOME_DIST1, IDC_EDIT_HOME_DIST2, IDC_EDIT_HOME_DIST3 };
        for (int i = 0; i < 3; ++i)
        {
            if (id == dirIds[i] || id == highIds[i] || id == lowIds[i] ||
                id == accIds[i] || id == decIds[i] || id == distIds[i])
            {
                m_homeConfirmed[i + 1] = false;
                CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + i, BST_UNCHECKED);
                UpdateUiState();
                return TRUE;
            }
        }
    }
    if (id == IDC_COMBO_MODE && code == CBN_SELCHANGE)
    {
        if (m_uiInitialized || InterlockedCompareExchange(&m_busy, 0, 0) != 0)
        {
            ::SendMessageW(FindControlHwnd(IDC_COMBO_MODE), CB_SETCURSEL, m_demoMode ? 1 : 0, 0);
            AppendLogUi(L"硬件/演示模式必须在初始化控制器前选择；模式切换需要重启程序。");
            return TRUE;
        }
        const int selected = (int)::SendMessageW(FindControlHwnd(IDC_COMBO_MODE), CB_GETCURSEL, 0, 0);
        m_demoMode = selected == 1;
        InterlockedExchange(&m_demoCurtain, 0);
        InterlockedExchange(&m_demoStop, 0);
        CheckDlgButton(IDC_CHECK_DEMO_CURTAIN, BST_UNCHECKED);
        CheckDlgButton(IDC_CHECK_DEMO_CURTAIN_SETTINGS, BST_UNCHECKED);
        CheckDlgButton(IDC_CHECK_DEMO_STOP, BST_UNCHECKED);
        CheckDlgButton(IDC_CHECK_DEMO_STOP_SETTINGS, BST_UNCHECKED);
        SaveSettings();
        AppendLogUi(m_demoMode ? L"已选择隔离演示模式：本模式不会调用控制卡 API 或真实 IO。"
                               : L"已选择硬件控制模式。请确认设备、接线和安全回路。");
        UpdateUiState();
        return TRUE;
    }
    if (id == IDC_CHECK_DEMO_RODLESS && code == BN_CLICKED)
    {
        if (!m_demoMode)
        {
            const bool active = ((InterlockedCompareExchange(&m_simExtInputs, 0, 0) & 1) != 0) ==
                                m_rodlessInPositionActiveHigh;
            CheckDlgButton(IDC_CHECK_DEMO_RODLESS, active ? BST_CHECKED : BST_UNCHECKED);
            AppendLogUi(L"DI0 模拟开关只在隔离演示模式可用。");
            return TRUE;
        }
        const bool active = IsDlgButtonChecked(IDC_CHECK_DEMO_RODLESS) == BST_CHECKED;
        const LONG raw = active == m_rodlessInPositionActiveHigh ? 1 : 0;
        InterlockedExchange(&m_simExtInputs, raw);
        AppendLogUi(active ? L"演示 DI0 已置为到位有效。" : L"演示 DI0 已置为未到位，可用于验证互锁/超时。");
        return TRUE;
    }
    if ((id == IDC_COMBO_AXIS_X || id == IDC_COMBO_AXIS_Y || id == IDC_COMBO_AXIS_Z) &&
        code == CBN_SELCHANGE)
    {
        const int index = id == IDC_COMBO_AXIS_X ? 0 : (id == IDC_COMBO_AXIS_Y ? 1 : 2);
        if (m_uiInitialized || InterlockedCompareExchange(&m_busy, 0, 0) != 0)
        {
            ::SendMessageW(FindControlHwnd(id), CB_SETCURSEL, m_axisForXyz[index] - 1, 0);
            AppendLogUi(L"坐标轴映射只能在控制器初始化前调整。");
            return TRUE;
        }
        const short selected = (short)(::SendMessageW(FindControlHwnd(id), CB_GETCURSEL, 0, 0) + 1);
        short candidate[3] = { m_axisForXyz[0], m_axisForXyz[1], m_axisForXyz[2] };
        candidate[index] = selected;
        if (candidate[0] == candidate[1] || candidate[0] == candidate[2] || candidate[1] == candidate[2])
        {
            ::SendMessageW(FindControlHwnd(id), CB_SETCURSEL, m_axisForXyz[index] - 1, 0);
            AppendLogUi(L"X、Y、Z 映射必须选择三个不同的物理轴。");
            return TRUE;
        }
        for (int i = 0; i < 3; ++i) m_axisForXyz[i] = candidate[i];
        SaveSettings();
        return TRUE;
    }
    if (code == BN_CLICKED)
    {
        if (id >= IDC_CHECK_HOME_CONFIRMED_1 && id <= IDC_CHECK_HOME_CONFIRMED_3)
        {
            const int axis = id - IDC_CHECK_HOME_CONFIRMED_1 + 1;
            const bool requested = IsDlgButtonChecked(id) == BST_CHECKED;
            if (m_demoMode || !m_uiInitialized || !m_homeDiagnosticsReceived[axis] ||
                m_homeInputReadRc != 0 || InterlockedCompareExchange(&m_busy, 0, 0) != 0)
            {
                m_homeConfirmed[axis] = false;
                CheckDlgButton(id, BST_UNCHECKED);
                AppendLogUi(L"HOME 确认未接受：需先初始化并成功读取 HOME 参数、输入和限位，且任务空闲。演示模式不确认真实硬件参数。");
            }
            else if (requested)
            {
                AxisHomeSettings current = {};
                if (!ReadHomeSettings((short)axis, current))
                {
                    m_homeConfirmed[axis] = false;
                    CheckDlgButton(id, BST_UNCHECKED);
                    AppendLogUi(L"HOME 参数无效，未接受该轴确认。请先修正方向、速度、加减速和搜索距离。");
                }
                else
                {
                    m_homeSettings[axis] = current;
                    m_homeConfirmed[axis] = true;
                    m_homeConfirmedSettings[axis] = current;
                    m_homeConfirmedSettings[axis].confirmationRequired = true;
                    m_homeConfirmedSettings[axis].confirmedTriggerIndex = m_homeTriggerIndex[axis];
                    m_homeConfirmedSettings[axis].confirmedEdge = m_homeTriggerEdge[axis];
                    m_homeConfirmedSettings[axis].confirmedControllerDirection =
                        m_homeControllerDirection[axis];
                    SaveSettings();
                    const short effectiveTrigger = current.overrideTriggerIndex
                        ? current.triggerIndex : m_homeTriggerIndex[axis];
                    const short effectiveEdge = current.overrideEdge
                        ? current.edge : m_homeTriggerEdge[axis];
                    CString text;
                    text.Format(_T("已现场核对 %d 轴 HOME：有效触发器=%d，捕获沿=%d，搜索方向=%d，原始 GPI=0x%08lX；请同时确认该轴限位未触发。"),
                                axis, effectiveTrigger, effectiveEdge,
                                current.direction, m_homeRawInputs);
                    AppendLogUi(text);
                }
            }
            else
            {
                m_homeConfirmed[axis] = false;
                AppendLogUi(L"已撤销该轴 HOME 现场确认，硬件回零按钮重新锁止。");
            }
            UpdateUiState();
            return TRUE;
        }
        if (id == IDC_CHECK_OPERATOR_SAFE)
        {
            if (!OperatorConfirmed() && InterlockedCompareExchange(&m_busy, 0, 0) != 0)
            {
                InterlockedExchange(&m_stopRequested, 1);
                AppendLogUi(L"操作员安全确认已取消，已请求当前任务停止。");
            }
            UpdateUiState();
            return TRUE;
        }
        if (id == IDC_CHECK_POLARITY_PRESS || id == IDC_CHECK_POLARITY_RODLESS ||
            id == IDC_CHECK_POLARITY_BIN2 || id == IDC_CHECK_POLARITY_BIN3)
        {
            const int index = id == IDC_CHECK_POLARITY_PRESS ? 0 :
                              (id == IDC_CHECK_POLARITY_RODLESS ? 1 :
                              (id == IDC_CHECK_POLARITY_BIN2 ? 2 : 3));
            if (m_uiInitialized || InterlockedCompareExchange(&m_busy, 0, 0) != 0)
            {
                CheckDlgButton(id, m_extendLevelHigh[index] ? BST_CHECKED : BST_UNCHECKED);
                AppendLogUi(L"输出极性只允许在控制器初始化前修改；请重启后调整。");
                return TRUE;
            }
            m_extendLevelHigh[0] = IsDlgButtonChecked(IDC_CHECK_POLARITY_PRESS) == BST_CHECKED;
            m_extendLevelHigh[1] = IsDlgButtonChecked(IDC_CHECK_POLARITY_RODLESS) == BST_CHECKED;
            m_extendLevelHigh[2] = IsDlgButtonChecked(IDC_CHECK_POLARITY_BIN2) == BST_CHECKED;
            m_extendLevelHigh[3] = IsDlgButtonChecked(IDC_CHECK_POLARITY_BIN3) == BST_CHECKED;
            m_polarityConfirmed = false;
            CheckDlgButton(IDC_CHECK_POLARITY, BST_UNCHECKED);
            SaveSettings();
            UpdateUiState();
            return TRUE;
        }
        if (id == IDC_CHECK_RESET_PRESS || id == IDC_CHECK_RESET_RODLESS ||
            id == IDC_CHECK_RESET_BIN2 || id == IDC_CHECK_RESET_BIN3)
        {
            const int index = id == IDC_CHECK_RESET_PRESS ? 0 :
                              (id == IDC_CHECK_RESET_RODLESS ? 1 :
                              (id == IDC_CHECK_RESET_BIN2 ? 2 : 3));
            if (m_uiInitialized || InterlockedCompareExchange(&m_busy, 0, 0) != 0)
            {
                CheckDlgButton(id, m_resetExtend[index] ? BST_CHECKED : BST_UNCHECKED);
                AppendLogUi(L"气缸复位目标只允许在初始化前修改；请重启后调整。");
                return TRUE;
            }
            m_resetExtend[index] = IsDlgButtonChecked(id) == BST_CHECKED;
            m_polarityConfirmed = false;
            CheckDlgButton(IDC_CHECK_POLARITY, BST_UNCHECKED);
            SaveSettings();
            UpdateUiState();
            return TRUE;
        }
        if (id == IDC_CHECK_RODLESS_ACTIVE || id == IDC_CHECK_RODLESS_HOME_ACTIVE)
        {
            if (m_uiInitialized || InterlockedCompareExchange(&m_busy, 0, 0) != 0)
            {
                CheckDlgButton(id, id == IDC_CHECK_RODLESS_ACTIVE
                    ? (m_rodlessInPositionActiveHigh ? BST_CHECKED : BST_UNCHECKED)
                    : (m_rodlessHomeActiveHigh ? BST_CHECKED : BST_UNCHECKED));
                AppendLogUi(L"无杆气缸端位输入极性只允许在初始化前修改；请重启后调整。");
                return TRUE;
            }
            if (id == IDC_CHECK_RODLESS_ACTIVE)
                m_rodlessInPositionActiveHigh = IsDlgButtonChecked(id) == BST_CHECKED;
            else
                m_rodlessHomeActiveHigh = IsDlgButtonChecked(id) == BST_CHECKED;
            SaveSettings();
            return TRUE;
        }
        if (id == IDC_CHECK_POLARITY)
        {
            if (InterlockedCompareExchange(&m_busy, 0, 0) != 0)
            {
                const bool requested = IsDlgButtonChecked(IDC_CHECK_POLARITY) == BST_CHECKED;
                if (!requested)
                {
                    m_polarityConfirmed = false;
                    InterlockedExchange(&m_stopRequested, 1);
                    AppendLogUi(L"确认已撤销，已请求当前流程停止；气缸输出保持当前状态。");
                }
                else
                {
                    CheckDlgButton(IDC_CHECK_POLARITY, BST_UNCHECKED);
                    AppendLogUi(L"流程运行期间不能更改极性确认状态。");
                }
                UpdateUiState();
                return TRUE;
            }
            m_polarityConfirmed = IsDlgButtonChecked(IDC_CHECK_POLARITY) == BST_CHECKED;
            SaveSettings();
            AppendLogUi(m_polarityConfirmed ? L"已确认气缸输出极性与复位目标。请仅在已核对接线和气路后勾选。"
                                            : L"气缸输出极性确认已撤销，复位和自动抓放已锁止。");
            UpdateUiState();
            return TRUE;
        }
        if (id == IDC_CHECK_LIGHT_ACTIVE || id == IDC_CHECK_STOP_ACTIVE)
        {
            if (InterlockedCompareExchange(&m_busy, 0, 0) != 0 || m_uiServoEnabled)
            {
                CheckDlgButton(id, (id == IDC_CHECK_LIGHT_ACTIVE ? m_lightCurtainActiveHigh : m_stopInputActiveHigh) ? BST_CHECKED : BST_UNCHECKED);
                AppendLogUi(L"安全输入极性只能在任务空闲、三轴伺服关闭时修改。");
                return TRUE;
            }
            if (!m_uiInitialized)
            {
                m_lightCurtainActiveHigh = IsDlgButtonChecked(IDC_CHECK_LIGHT_ACTIVE) == BST_CHECKED;
                m_stopInputActiveHigh = IsDlgButtonChecked(IDC_CHECK_STOP_ACTIVE) == BST_CHECKED;
                SaveSettings();
            }
            else AppendLogUi(L"极性已暂存。点击“应用安全输入极性”后由后台线程应用；该操作不会解除联锁。");
            return TRUE;
        }
        if (id == IDC_CHECK_DEMO_CURTAIN || id == IDC_CHECK_DEMO_CURTAIN_SETTINGS)
        {
            const bool requested = IsDlgButtonChecked(id) == BST_CHECKED;
            if (!m_demoMode)
            {
                CheckDlgButton(IDC_CHECK_DEMO_CURTAIN, BST_UNCHECKED);
                CheckDlgButton(IDC_CHECK_DEMO_CURTAIN_SETTINGS, BST_UNCHECKED);
                AppendLogUi(L"光幕模拟只在隔离演示模式下可用。");
            }
            else
            {
                CheckDlgButton(IDC_CHECK_DEMO_CURTAIN, requested ? BST_CHECKED : BST_UNCHECKED);
                CheckDlgButton(IDC_CHECK_DEMO_CURTAIN_SETTINGS, requested ? BST_CHECKED : BST_UNCHECKED);
                InterlockedExchange(&m_demoCurtain, requested ? 1 : 0);
                if (requested)
                {
                    m_safetyTripped = true;
                    m_safetySource |= GTS_SAFETY_LIGHT_CURTAIN;
                    InterlockedExchange(&m_stopRequested, 1);
                }
                AppendLogUi(requested ? L"演示光幕输入已触发；运行任务会立即停止，气缸状态保持。"
                                      : L"演示光幕输入已恢复；请在设置诊断页清除联锁。");
            }
            UpdateUiState();
            return TRUE;
        }
        if (id == IDC_CHECK_DEMO_STOP || id == IDC_CHECK_DEMO_STOP_SETTINGS)
        {
            const bool requested = IsDlgButtonChecked(id) == BST_CHECKED;
            if (!m_demoMode)
            {
                CheckDlgButton(IDC_CHECK_DEMO_STOP, BST_UNCHECKED);
                CheckDlgButton(IDC_CHECK_DEMO_STOP_SETTINGS, BST_UNCHECKED);
                AppendLogUi(L"系统停止模拟只在隔离演示模式下可用。");
            }
            else
            {
                CheckDlgButton(IDC_CHECK_DEMO_STOP, requested ? BST_CHECKED : BST_UNCHECKED);
                CheckDlgButton(IDC_CHECK_DEMO_STOP_SETTINGS, requested ? BST_CHECKED : BST_UNCHECKED);
                InterlockedExchange(&m_demoStop, requested ? 1 : 0);
                if (requested)
                {
                    m_safetyTripped = true;
                    m_safetySource |= GTS_SAFETY_SYSTEM_STOP;
                    InterlockedExchange(&m_stopRequested, 1);
                }
                AppendLogUi(requested ? L"演示系统停止输入已触发；请求停轴并锁止新动作。"
                                      : L"演示系统停止输入已恢复；请先核实状态，再显式清报警。");
            }
            UpdateUiState();
            return TRUE;
        }
        if (id >= IDC_IO_ON_BASE && id < IDC_IO_ON_BASE + kOutputCount)
        {
            const int output = id - IDC_IO_ON_BASE;
            if (output >= GTS_OUT_PRESS_CYLINDER && !m_polarityConfirmed)
            {
                AppendLogUi(L"气缸输出已阻止：请先确认输出极性和复位目标。");
                return TRUE;
            }
            if (!OperatorConfirmed() || m_safetyTripped)
            {
                AppendLogUi(L"IO 输出已阻止：请确认现场安全状态并清除软件联锁。");
                return TRUE;
            }
            GtsCommandRequest request = DefaultRequest(GTS_CMD_IO_OUTPUT);
            request.output = output; request.outputOn = true;
            SubmitRequest(request);
            return TRUE;
        }
        if (id >= IDC_IO_OFF_BASE && id < IDC_IO_OFF_BASE + kOutputCount)
        {
            const int output = id - IDC_IO_OFF_BASE;
            if (output >= GTS_OUT_PRESS_CYLINDER && !m_polarityConfirmed)
            {
                AppendLogUi(L"气缸复位已阻止：请先确认输出极性和复位目标。");
                return TRUE;
            }
            if (m_safetyTripped)
            {
                AppendLogUi(L"安全联锁期间锁止普通 IO 输出，气缸保持当前状态。");
                return TRUE;
            }
            GtsCommandRequest request = DefaultRequest(GTS_CMD_IO_OUTPUT);
            request.output = output; request.outputOn = false;
            if (output == GTS_OUT_PRESS_CYLINDER) request.outputOn = request.resetExtend[0];
            else if (output == GTS_OUT_RODLESS) request.outputOn = request.resetExtend[1];
            else if (output == GTS_OUT_BIN2) request.outputOn = request.resetExtend[2];
            else if (output == GTS_OUT_BIN3) request.outputOn = request.resetExtend[3];
            SubmitRequest(request);
            return TRUE;
        }
        if (HandleButtonCommand(id)) return TRUE;
    }
    return CDialogEx::OnCommand(wParam, lParam);
}

BOOL CTrapDemoMFCDlg::HandleButtonCommand(int id)
{
    if (id == IDC_BTN_HOME_DIAG)
    {
        if (!m_uiInitialized)
        {
            AppendLogUi(L"请先初始化控制器后读取 HOME 状态。");
            return TRUE;
        }
        if (m_demoMode)
        {
            SetDlgItemText(IDC_STATIC_HOME_RAW,
                           _T("隔离演示模式：不会读取真实 GTS HOME 参数或控制器输入。"));
            AppendLogUi(L"演示模式不读取硬件 HOME 参数、DI 或轴限位状态，也不调用控制卡 API。");
            return TRUE;
        }
        GtsCommandRequest request = DefaultRequest(GTS_CMD_READ_HOME_DIAGNOSTICS);
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_APPLY_SAFETY_POLARITY)
    {
        if (InterlockedCompareExchange(&m_busy, 0, 0) != 0 || m_uiServoEnabled)
        {
            AppendLogUi(L"应用安全输入极性已阻止：请先停止任务并关闭全部轴伺服。");
            return TRUE;
        }
        const bool lightHigh = IsDlgButtonChecked(IDC_CHECK_LIGHT_ACTIVE) == BST_CHECKED;
        const bool stopHigh = IsDlgButtonChecked(IDC_CHECK_STOP_ACTIVE) == BST_CHECKED;
        if (!m_uiInitialized)
        {
            m_lightCurtainActiveHigh = lightHigh;
            m_stopInputActiveHigh = stopHigh;
            SaveSettings();
            AppendLogUi(L"安全输入极性已保存，将在下次初始化时采用；系统停止默认高有效未被自动推断。");
            return TRUE;
        }
        GtsCommandRequest request = DefaultRequest(GTS_CMD_APPLY_SAFETY_POLARITY);
        request.lightCurtainActiveHigh = lightHigh;
        request.stopInputActiveHigh = stopHigh;
        m_pendingLightCurtainActiveHigh = lightHigh;
        m_pendingStopInputActiveHigh = stopHigh;
        AppendLogUi(m_demoMode
            ? L"正在由隔离演示线程应用安全输入极性，不调用 GTS API 或真实 IO。"
            : L"正在由后台线程应用安全输入极性；联锁不会因此清除。");
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_INIT)
    {
        GtsCommandRequest request = DefaultRequest(GTS_CMD_INIT);
        request.demoMode = m_demoMode;
        AppendLogUi(m_demoMode ? L"启动隔离演示状态。" : L"正在初始化 GTS 控制器与 gLink200 模块。");
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_ENABLE)
    {
        if (!OperatorConfirmed() || m_safetyTripped || !m_safetyInputsValid)
        {
            AfxMessageBox(_T("请确认现场安全条件、等待 EXI1/EXI4 输入读取成功，并在联锁解除后再使能伺服。"));
            return TRUE;
        }
        GtsCommandRequest request = DefaultRequest(GTS_CMD_ENABLE);
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_DISABLE)
    {
        GtsCommandRequest request = DefaultRequest(GTS_CMD_DISABLE);
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_STOP || id == IDC_BTN_STOP_AUTO_PAGE)
    {
        if (InterlockedCompareExchange(&m_busy, 0, 0) != 0)
        {
            InterlockedExchange(&m_stopRequested, 1);
            AppendLogUi(L"已请求停止当前任务；等待工作线程发送控制器停止命令。");
        }
        return TRUE;
    }
    if (id == IDC_BTN_MOVE)
    {
        short axis = SelectedAxis();
        long pos = 0; double vel = 0.0, acc = 0.0, dec = 0.0;
        if (!ReadAxisMotionInputs(axis, pos, vel) || !ReadCommonAccDec(acc, dec))
        { AfxMessageBox(_T("请填写有效的目标位置、速度、加速度和减速度。")); return TRUE; }
        if (!OperatorConfirmed() || m_safetyTripped) { AfxMessageBox(_T("请先确认现场安全状态。")); return TRUE; }
        GtsCommandRequest request = DefaultRequest(GTS_CMD_MOVE_SINGLE);
        request.axis = axis; request.targets[axis] = pos; request.velocities[axis] = vel;
        request.acceleration = acc; request.deceleration = dec;
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_SEQUENCE)
    {
        GtsCommandRequest request = DefaultRequest(GTS_CMD_SEQUENCE);
        if (!ReadCommonAccDec(request.acceleration, request.deceleration))
        { AfxMessageBox(_T("请填写有效加速度和减速度。")); return TRUE; }
        for (short axis = 1; axis <= 3; ++axis)
            if (!ReadAxisMotionInputs(axis, request.targets[axis], request.velocities[axis]))
            { AfxMessageBox(_T("请为三轴分别填写目标位置和速度。")); return TRUE; }
        if (!OperatorConfirmed() || m_safetyTripped) { AfxMessageBox(_T("请先确认现场安全状态。")); return TRUE; }
        AppendLogUi(L"三轴依次运动作为单个后台任务执行；一键完成整个轴序列。");
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_HOME)
    {
        const short axis = SelectedAxis();
        GtsCommandRequest request = DefaultRequest(GTS_CMD_HOME_AXIS);
        request.axis = axis;
        if (!ReadHomeSettings(axis, request.home[axis]))
        { AfxMessageBox(_T("请检查所选轴 HOME 方向、高低速、加减速度和搜索距离。")); return TRUE; }
        m_homeSettings[axis] = request.home[axis]; SaveSettings();
        if (!m_demoMode &&
            (!m_homeDiagnosticsReceived[axis] || m_homeInputReadRc != 0 ||
             !m_homeConfirmed[axis]))
        {
            AfxMessageBox(_T("硬件回零已锁止。先读取 HOME 状态，核对控制器触发器/触发沿、原始输入、该轴限位和搜索方向，再勾选该轴“已核对”。"));
            return TRUE;
        }
        if (!m_demoMode)
        {
            const AxisHomeSettings& confirmed = m_homeConfirmedSettings[axis];
            if (!confirmed.confirmationRequired ||
                !SameHomeSettings(request.home[axis], confirmed))
            {
                m_homeConfirmed[axis] = false;
                CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + axis - 1, BST_UNCHECKED);
                UpdateUiState();
                AfxMessageBox(_T("HOME 参数与现场确认时不一致。请重新核对并勾选该轴确认。"));
                return TRUE;
            }
            request.home[axis].confirmationRequired = true;
            request.home[axis].confirmedTriggerIndex = confirmed.confirmedTriggerIndex;
            request.home[axis].confirmedEdge = confirmed.confirmedEdge;
            request.home[axis].confirmedControllerDirection =
                confirmed.confirmedControllerDirection;
        }
        if (!OperatorConfirmed() || m_safetyTripped) { AfxMessageBox(_T("回零前请确认报警、限位、光幕、急停和机械行程状态。")); return TRUE; }
        const short triggerIndex = request.home[axis].overrideTriggerIndex
            ? request.home[axis].triggerIndex : m_homeTriggerIndex[axis];
        const short triggerEdge = request.home[axis].overrideEdge
            ? request.home[axis].edge : m_homeTriggerEdge[axis];
        CString prompt;
        prompt.Format(_T("将对 %d 轴执行 HOME 搜索。有效触发器=%d，触发沿=%d，方向=%d，当前原始 GPI=0x%08lX。请确认 HOME 接线、方向和行程安全。继续？"),
                      axis, triggerIndex, triggerEdge,
                      request.home[axis].direction, m_homeRawInputs);
        if (AfxMessageBox(prompt, MB_YESNO | MB_ICONWARNING) != IDYES) return TRUE;
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_HOME_SEQUENCE || id == IDC_BTN_HOME_SEQUENCE_MANUAL ||
        id == IDC_BTN_HOME_RESET || id == IDC_BTN_HOME_RESET_MANUAL)
    {
        GtsCommandRequest request = DefaultRequest(GTS_CMD_HOME_SEQUENCE);
        request.resetOutputs = id == IDC_BTN_HOME_RESET || id == IDC_BTN_HOME_RESET_MANUAL;
        if (!ReadAllHomeSettings(request.home))
        { AfxMessageBox(_T("请检查三轴各自的 HOME 搜索参数。")); return TRUE; }
        for (int axis = 1; axis <= 3; ++axis) m_homeSettings[axis] = request.home[axis];
        SaveSettings();
        if (!m_demoMode &&
            (!m_homeConfirmed[1] || !m_homeConfirmed[2] || !m_homeConfirmed[3] ||
             !m_homeDiagnosticsReceived[1] || !m_homeDiagnosticsReceived[2] ||
             !m_homeDiagnosticsReceived[3] || m_homeInputReadRc != 0))
        {
            AfxMessageBox(_T("硬件三轴回零已锁止。需逐轴读取并核对 HOME 触发器、触发沿、方向和限位状态，再分别勾选三轴确认。"));
            return TRUE;
        }
        if (!m_demoMode)
        {
            for (int axis = 1; axis <= 3; ++axis)
            {
                const AxisHomeSettings& confirmed = m_homeConfirmedSettings[axis];
                if (!confirmed.confirmationRequired ||
                    !SameHomeSettings(request.home[axis], confirmed))
                {
                    m_homeConfirmed[axis] = false;
                    CheckDlgButton(IDC_CHECK_HOME_CONFIRMED_1 + axis - 1, BST_UNCHECKED);
                    UpdateUiState();
                    AfxMessageBox(_T("HOME 参数与现场确认时不一致。请重新核对并勾选对应轴确认。"));
                    return TRUE;
                }
                request.home[axis].confirmationRequired = true;
                request.home[axis].confirmedTriggerIndex = confirmed.confirmedTriggerIndex;
                request.home[axis].confirmedEdge = confirmed.confirmedEdge;
                request.home[axis].confirmedControllerDirection =
                    confirmed.confirmedControllerDirection;
            }
        }
        if (!OperatorConfirmed() || m_safetyTripped) { AfxMessageBox(_T("回零前请确认三轴限位、光幕、急停和机械行程状态。")); return TRUE; }
        if (request.resetOutputs && !m_polarityConfirmed)
        { AfxMessageBox(_T("请先核对各气缸输出极性并在设置页确认。")); return TRUE; }
        if (AfxMessageBox(_T("将按 3→1→2 依次 HOME；任一轴失败、限位或停止请求都会取消后续轴。请再次确认三轴 HOME 搜索方向及现场行程。继续？"), MB_YESNO | MB_ICONWARNING) != IDYES) return TRUE;
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_CLEAR_ALARMS || id == IDC_BTN_CLEAR_ALARMS_SETTINGS)
    {
        GtsCommandRequest request = DefaultRequest(GTS_CMD_CLEAR_ALARMS);
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_ZERO_AXIS || id == IDC_BTN_ZERO_AXIS_SETTINGS)
    {
        GtsCommandRequest request = DefaultRequest(GTS_CMD_ZERO_AXIS);
        request.axis = SelectedAxis();
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_RESET_OUTPUTS_PAGE)
    {
        if (!m_polarityConfirmed) { AfxMessageBox(_T("请先确认气缸输出极性和复位目标。")); return TRUE; }
        GtsCommandRequest request = DefaultRequest(GTS_CMD_RESET_OUTPUTS);
        if (AfxMessageBox(_T("将关闭指示灯/蜂鸣器并按配置命令各气缸收回。气缸无独立到位反馈，确认现场安全后继续？"), MB_YESNO | MB_ICONWARNING) != IDYES) return TRUE;
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_START_AUTO || id == IDC_BTN_AUTO_START_PAGE)
    {
        GtsCommandRequest request = DefaultRequest(GTS_CMD_AUTO_PICK_PLACE);
        if (!ReadRecipe(request.recipe))
        { AfxMessageBox(_T("请先示教抓取位、放置位和安全零位，并填写有效轨迹速度/加速度。")); return TRUE; }
        long dwell = 0, timeout = 0;
        if (!ReadLongValue(IDC_EDIT_CYLINDER_DWELL, dwell) || dwell <= 0 ||
            !ReadLongValue(IDC_EDIT_RODLESS_TIMEOUT, timeout) || timeout <= 0)
        { AfxMessageBox(_T("气缸动作延时和无杆 DI0 等待超时必须为正整数毫秒。")); return TRUE; }
        request.cylinderDwellMs = (DWORD)dwell; request.rodlessTimeoutMs = (DWORD)timeout;
        m_cylinderDwellMs = request.cylinderDwellMs; m_rodlessTimeoutMs = request.rodlessTimeoutMs; SaveSettings();
        if (!m_extensionReady) { AfxMessageBox(_T("gLink200 未连接，自动抓放已禁用。")); return TRUE; }
        if (!m_polarityConfirmed) { AfxMessageBox(_T("请先确认气缸输出极性。")); return TRUE; }
        if (!OperatorConfirmed() || m_safetyTripped) { AfxMessageBox(_T("请确认现场安全状态并解除软件联锁。")); return TRUE; }
        if (AfxMessageBox(_T("将执行一次完整抓放周期。开环步进无法确认机械位置；请低速、有人监护并确认气路安全。继续？"), MB_YESNO | MB_ICONWARNING) != IDYES) return TRUE;
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_TEACH_PICK || id == IDC_BTN_TEACH_PLACE || id == IDC_BTN_TEACH_SAFE)
    {
        if (!m_uiInitialized || m_safetyTripped) { AfxMessageBox(_T("示教前请初始化并解除安全联锁。")); return TRUE; }
        GtsCommandRequest request = DefaultRequest(GTS_CMD_CAPTURE_POSITION);
        request.captureSlot = id == IDC_BTN_TEACH_PICK ? GTS_CAPTURE_PICK : (id == IDC_BTN_TEACH_PLACE ? GTS_CAPTURE_PLACE : GTS_CAPTURE_SAFE);
        AppendLogUi(L"正在读取三轴规划位置用于示教；开环设备不能自动检测丢步。");
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_TRAJ_LINE || id == IDC_BTN_TRAJ_ARC ||
        id == IDC_BTN_TRAJ_TRIANGLE || id == IDC_BTN_TRAJ_CIRCLE)
    {
        GtsCommandRequest request = DefaultRequest(GTS_CMD_TRAJECTORY);
        request.trajectory.kind = id == IDC_BTN_TRAJ_LINE ? GTS_TRAJ_LINE :
                                  (id == IDC_BTN_TRAJ_ARC ? GTS_TRAJ_ARC :
                                  (id == IDC_BTN_TRAJ_TRIANGLE ? GTS_TRAJ_TRIANGLE : GTS_TRAJ_CIRCLE));
        if (!ReadTrajectory(request.trajectory) ||
            ((request.trajectory.kind == GTS_TRAJ_TRIANGLE || request.trajectory.kind == GTS_TRAJ_CIRCLE) && request.trajectory.radius <= 0))
        { AfxMessageBox(_T("请填写有效的轨迹坐标、圆心、半径、速度和加速度。")); return TRUE; }
        if (!OperatorConfirmed() || m_safetyTripped) { AfxMessageBox(_T("执行轨迹前请确认现场安全条件。")); return TRUE; }
        if (AfxMessageBox(_T("将执行三轴坐标系插补。请确认轨迹范围、软限位和机械干涉。继续？"), MB_YESNO | MB_ICONWARNING) != IDYES) return TRUE;
        return SubmitRequest(request);
    }
    if (id == IDC_BTN_IO_REFRESH || id == IDC_BTN_IO_REFRESH_PAGE)
    {
        if (m_demoMode) { PublishDemoStatus(); PublishDemoIo(); }
        else AppendLogUi(L"IO 状态由后台工作线程定时刷新。");
        return TRUE;
    }
    if (id == IDC_BTN_CLEAR_LOG)
    {
        ClearLogUi();
        return TRUE;
    }
    return FALSE;
}

void CTrapDemoMFCDlg::DrainOwnedMessages()
{
    MSG msg;
    while (::PeekMessage(&msg, m_hWnd, WM_GTS_MOTION_LOG, WM_GTS_CAPTURE_POS, PM_REMOVE))
    {
        if (msg.message == WM_GTS_MOTION_LOG && msg.lParam)
            delete[] reinterpret_cast<wchar_t*>(msg.lParam);
        else if (msg.message == WM_GTS_AXIS_STATUS || msg.message == WM_GTS_IO_STATUS ||
                msg.message == WM_GTS_PROGRESS || msg.message == WM_GTS_CAPTURE_POS)
        {
            if (msg.lParam)
            {
                if (msg.message == WM_GTS_PROGRESS) delete reinterpret_cast<GtsProgressPacket*>(msg.lParam);
                else if (msg.message == WM_GTS_CAPTURE_POS) delete reinterpret_cast<GtsCapturePositionPacket*>(msg.lParam);
                else delete reinterpret_cast<GtsAxisStatusPacket*>(msg.lParam);
            }
        }
    }
}

void CTrapDemoMFCDlg::OnDestroy()
{
    m_closing = true;
    SaveSettings();
    InterlockedExchange(&m_stopRequested, 1);
    InterlockedExchange(&m_shutdown, 1);
    m_commandEvent.SetEvent();
    if (m_pWorker)
    {
        WaitForSingleObject(m_pWorker->m_hThread, INFINITE);
        delete m_pWorker;
        m_pWorker = NULL;
    }
    DrainOwnedMessages();
    CDialogEx::OnDestroy();
}
