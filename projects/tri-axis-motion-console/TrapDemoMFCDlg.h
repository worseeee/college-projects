#pragma once

#include <afxwin.h>
#include <afxcmn.h>
#include <afxmt.h>
#include <vector>
#include "GtMotionController.h"
#include "JogHoldButton.h"
#include "resource.h"

enum GtsWorkerCommand
{
    GTS_CMD_NONE = 0,
    GTS_CMD_INIT,
    GTS_CMD_ENABLE,
    GTS_CMD_MOVE_SINGLE,
    GTS_CMD_SEQUENCE,
    GTS_CMD_JOG,
    GTS_CMD_HOME_AXIS,
    GTS_CMD_HOME_SEQUENCE,
    GTS_CMD_CLEAR_ALARMS,
    GTS_CMD_ZERO_AXIS,
    GTS_CMD_IO_OUTPUT,
    GTS_CMD_AUTO_PICK_PLACE,
    GTS_CMD_TRAJECTORY,
    GTS_CMD_CAPTURE_POSITION,
    GTS_CMD_RESET_OUTPUTS,
    GTS_CMD_DISABLE,
    GTS_CMD_APPLY_SAFETY_POLARITY,
    GTS_CMD_READ_HOME_DIAGNOSTICS
};

enum GtsCaptureSlot
{
    GTS_CAPTURE_PICK = 1,
    GTS_CAPTURE_PLACE = 2,
    GTS_CAPTURE_SAFE = 3
};

struct GtsCommandRequest
{
    LONG command;
    short axis;
    int direction;
    long targets[4];
    double velocities[4];
    double acceleration;
    double deceleration;
    AxisHomeSettings home[4];
    GtsTrajectoryRequest trajectory;
    GtsPickPlaceRecipe recipe;
    DWORD cylinderDwellMs;
    DWORD rodlessTimeoutMs;
    int output;
    bool outputOn;
    int captureSlot;
    bool resetOutputs;
    bool extendLevelHigh[4]; // [0]=press, [1]=rodless, [2]=bin2, [3]=bin3
    bool resetExtend[4];     // configured logical target for each cylinder reset
    bool polarityConfirmed;
    bool demoMode;
    bool lightCurtainActiveHigh;
    bool stopInputActiveHigh;
    bool rodlessInPositionActiveHigh;
    bool rodlessHomeActiveHigh;
    short axisForXyz[3];
};

class CPageViewport : public CWnd
{
public:
    CPageViewport();
    BOOL Create(CWnd* parent, UINT id);
    void RegisterControl(HWND hwnd, const RECT& logicalRect);
    void SetLayoutScale(double scale);
    void SetContentSize(int width, int height);
    void ResetScroll();

protected:
    virtual BOOL OnCommand(WPARAM wParam, LPARAM lParam);
    virtual BOOL OnNotify(WPARAM wParam, LPARAM lParam, LRESULT* pResult);
    afx_msg LRESULT OnJogButtonDown(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnJogButtonUp(WPARAM wParam, LPARAM lParam);
    afx_msg void OnHScroll(UINT code, UINT position, CScrollBar* bar);
    afx_msg void OnVScroll(UINT code, UINT position, CScrollBar* bar);
    DECLARE_MESSAGE_MAP()

private:
    struct ChildLayout { HWND hwnd; RECT rect; };
    int m_contentWidth;
    int m_contentHeight;
    int m_scrollX;
    int m_scrollY;
    double m_scale;
    std::vector<ChildLayout> m_children;
    void ScrollTo(int x, int y);
    void LayoutChildren();
};

class CTrapDemoMFCDlg : public CDialogEx
{
public:
    explicit CTrapDemoMFCDlg(CWnd* pParent = NULL);
    enum { IDD = IDD_TRAPDEMOMFC_DIALOG };

protected:
    virtual void DoDataExchange(CDataExchange* pDX);
    virtual BOOL OnInitDialog();
    virtual BOOL OnCommand(WPARAM wParam, LPARAM lParam);
    DECLARE_MESSAGE_MAP()

private:
    struct LayoutEntry { HWND hwnd; RECT rect; int page; };

    CWinThread* m_pWorker;
    CEvent m_commandEvent;
    CCriticalSection m_commandLock;
    GtsCommandRequest m_request;

    volatile LONG m_busy;
    volatile LONG m_stopRequested;
    volatile LONG m_shutdown;
    volatile LONG m_activeCommand;
    volatile LONG m_activeJogDirection;
    volatile LONG m_demoCurtain;
    volatile LONG m_demoStop;
    short m_lastCommandAxis;

    bool m_uiInitialized;
    bool m_uiServoEnabled;
    bool m_extensionReady;
    bool m_closing;
    bool m_demoMode;
    bool m_safetyTripped;
    bool m_safetyInputsValid;
    int m_safetySource;
    bool m_polarityConfirmed;
    bool m_lightCurtainActiveHigh;
    bool m_stopInputActiveHigh;
    bool m_pendingLightCurtainActiveHigh;
    bool m_pendingStopInputActiveHigh;
    bool m_rodlessInPositionActiveHigh;
    bool m_rodlessHomeActiveHigh;
    short m_axisForXyz[3];
    bool m_axisHomed[4];
    bool m_homeConfirmed[4];
    bool m_homeDiagnosticsReceived[4];
    short m_homeTriggerIndex[4];
    short m_homeTriggerEdge[4];
    short m_homeControllerDirection[4];
    long m_homeRawInputs;
    short m_homeInputReadRc;
    bool m_taught[4]; // slots 1=pick, 2=place, 3=safe
    long m_taughtPositions[4][4];
    AxisHomeSettings m_homeSettings[4];
    AxisHomeSettings m_homeConfirmedSettings[4];
    bool m_extendLevelHigh[4];
    bool m_resetExtend[4];
    DWORD m_cylinderDwellMs;
    DWORD m_rodlessTimeoutMs;
    int m_activePage;

    // Simulation state is only accessed by the worker except for the light-curtain request.
    bool m_simInitialized;
    bool m_simEnabled[4];
    bool m_simHomed[4];
    long m_simPosition[4];
    long m_simInputs;
    long m_simOutputs;
    volatile LONG m_simExtInputs;
    unsigned short m_simExtOutputs;

    CTabCtrl m_tab;
    CPageViewport m_pageViewports[6];
    CListCtrl m_axisStatusList;
    CEdit m_logEdit;
    CJogHoldButton m_btnJogNegative;
    CJogHoldButton m_btnJogPositive;
    CFont m_uiFont;
    CBrush m_backgroundBrush;
    std::vector<LayoutEntry> m_layoutEntries;
    std::vector<int> m_outputStatusIds;
    std::vector<int> m_inputStatusIds;
    std::vector<int> m_extInputStatusIds;
    std::vector<int> m_inputBitNumbers;
    std::vector<int> m_extInputBitNumbers;
    int m_progressLabelId;
    int m_controllerStatusId;
    int m_hardwareStatusId;
    int m_extensionStatusId;
    int m_feedbackStatusId;

    CGtMotionController m_motion;

    static UINT WorkerThreadProc(LPVOID pParam);
    UINT WorkerLoop();
    short RunDemoCommand(const GtsCommandRequest& request);
    void PublishDemoStatus();
    void PublishDemoIo();

    BOOL SubmitRequest(const GtsCommandRequest& request, bool resetStopFlag = true);
    GtsCommandRequest DefaultRequest(LONG command) const;
    bool ReadLongValue(int controlId, long& value) const;
    bool ReadPositiveDouble(int controlId, double& value,
                            double maxValue = 20.0) const;
    bool ReadAxisMotionInputs(short axis, long& pos, double& vel) const;
    bool ReadCommonAccDec(double& acc, double& dec) const;
    bool ReadHomeSettings(short axis, AxisHomeSettings& settings) const;
    bool ReadAllHomeSettings(AxisHomeSettings settings[4]) const;
    bool ReadTrajectory(GtsTrajectoryRequest& trajectory) const;
    bool ReadRecipe(GtsPickPlaceRecipe& recipe) const;

    void CreateUi();
    HWND AddControl(int page, int id, LPCWSTR className, LPCWSTR text,
                    DWORD style, int x, int y, int width, int height,
                    DWORD exStyle = 0);
    HWND AddLabel(int page, int id, LPCWSTR text, int x, int y, int width, int height);
    HWND AddButton(int page, int id, LPCWSTR text, int x, int y, int width, int height,
                   DWORD style = BS_PUSHBUTTON);
    HWND AddEdit(int page, int id, LPCWSTR value, int x, int y, int width, int height,
                 DWORD extraStyle = 0);
    HWND AddCheck(int page, int id, LPCWSTR text, int x, int y, int width, int height,
                  bool checked = false);
    HWND AddGroup(int page, int id, LPCWSTR text, int x, int y, int width, int height);
    void AddIoRow(int row, int output, LPCWSTR name, int page, int x, int y,
                  bool extension = false);
    void InitAxisStatusList();
    void ApplyPageVisibility(int page);
    void LayoutUi(int width, int height);
    CWnd* GetDlgItem(int nID) const;
    int GetDlgItemText(int nID, CString& text) const;
    UINT IsDlgButtonChecked(int nID) const;
    void CheckDlgButton(int nID, UINT state);
    BOOL SetDlgItemText(int nID, LPCTSTR text);
    HWND FindControlHwnd(int nID) const;
    void LoadSettings();
    void SaveSettings() const;
    CString SettingsPath() const;
    bool OperatorConfirmed() const;
    short SelectedAxis() const;
    void AppendLogUi(const wchar_t* text);
    void ClearLogUi();
    void UpdateUiState();
    void UpdateIoLabels(const GtsIoStatusPacket& packet);
    void UpdateCaptureState(const GtsCapturePositionPacket& packet);
    void DrainOwnedMessages();

    afx_msg LRESULT OnMotionLog(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnMotionDone(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnJogButtonDown(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnJogButtonUp(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnAxisStatus(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnIoStatus(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnProgress(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnCapturePosition(WPARAM wParam, LPARAM lParam);
    afx_msg LRESULT OnHomeDiagnostics(WPARAM wParam, LPARAM lParam);
    afx_msg void OnTabChanged(NMHDR* pNMHDR, LRESULT* pResult);
    afx_msg void OnSize(UINT nType, int cx, int cy);
    afx_msg void OnGetMinMaxInfo(MINMAXINFO* pMMI);
    afx_msg void OnDestroy();

    BOOL HandleButtonCommand(int id);
};
