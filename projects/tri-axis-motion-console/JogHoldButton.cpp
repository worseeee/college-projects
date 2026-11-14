#include "pch.h" // Replace with stdafx.h if your project uses the older MFC precompiled header.
#include "JogHoldButton.h"

BEGIN_MESSAGE_MAP(CJogHoldButton, CButton)
    ON_WM_LBUTTONDOWN()
    ON_WM_LBUTTONUP()
    ON_WM_CAPTURECHANGED()
    ON_WM_CANCELMODE()
END_MESSAGE_MAP()
