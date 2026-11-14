#pragma once
#include <Windows.h>

#define WM_GTS_MOTION_LOG       (WM_APP + 101)
#define WM_GTS_MOTION_DONE      (WM_APP + 102)
#define WM_GTS_JOG_BUTTON_DOWN  (WM_APP + 103)
#define WM_GTS_JOG_BUTTON_UP    (WM_APP + 104)
#define WM_GTS_AXIS_STATUS      (WM_APP + 105)
#define WM_GTS_IO_STATUS        (WM_APP + 106)
#define WM_GTS_PROGRESS         (WM_APP + 107)
#define WM_GTS_CAPTURE_POS      (WM_APP + 108)
#define WM_GTS_HOME_DIAGNOSTICS (WM_APP + 109)

enum GtsSafetySource
{
    GTS_SAFETY_NONE = 0,
    GTS_SAFETY_SYSTEM_STOP = 1,
    GTS_SAFETY_LIGHT_CURTAIN = 2
};

struct GtsAxisStatusRow
{
    long status;
    double prfPos;
    short statusRc;
    short prfRc;
};

struct GtsAxisStatusPacket
{
    bool initialized;
    bool opened;
    bool extensionReady;
    bool axisEnabled[3];
    GtsAxisStatusRow rows[3];
};

struct GtsIoStatusPacket
{
    long directInputs;
    long directOutputs;
    unsigned short extensionInputs;
    unsigned short extensionOutputs;
    short directInputRc;
    short directOutputRc;
    short extensionInputRc;
    short extensionOutputRc;
    bool extensionReady;
    bool safetyActive;
    bool stopInputRaw;
    bool lightCurtainRaw;
    bool stopInputActive;
    bool lightCurtainActive;
    int safetySource;
};

struct GtsProgressPacket
{
    int step;
    int total;
    wchar_t text[192];
};

struct GtsCapturePositionPacket
{
    int slot;
    short result;
    long positions[4];
};

struct GtsHomeDiagnosticRow
{
    short axis;
    short homePrmRc;
    short statusRc;
    short homeStatusRc;
    short triggerIndex;
    short edge;
    short moveDir;
    short run;
    short stage;
    short error;
    long status;
    long capturePos;
    long targetPos;
};

struct GtsHomeDiagnosticsPacket
{
    short inputRc;
    long directInputs;
    GtsHomeDiagnosticRow rows[3];
};
