#pragma once
#include <afxwin.h>
#include "MotionMessages.h"

// A JOG button sends start on mouse-down and stop on mouse-up/capture loss.
class CJogHoldButton : public CButton
{
public:
    CJogHoldButton() : m_direction(1), m_tracking(false) {}
    void SetDirection(int direction) { m_direction = direction >= 0 ? 1 : -1; }

protected:
    int m_direction;
    bool m_tracking;

    void NotifyDown()
    {
        if (GetParent())
            GetParent()->PostMessage(WM_GTS_JOG_BUTTON_DOWN,
                (WPARAM)(INT_PTR)m_direction, (LPARAM)GetDlgCtrlID());
    }

    void NotifyUp()
    {
        if (!m_tracking) return;
        m_tracking = false;
        if (GetParent())
            GetParent()->PostMessage(WM_GTS_JOG_BUTTON_UP,
                (WPARAM)(INT_PTR)m_direction, (LPARAM)GetDlgCtrlID());
    }

    afx_msg void OnLButtonDown(UINT nFlags, CPoint point)
    {
        CButton::OnLButtonDown(nFlags, point);
        if (!m_tracking)
        {
            m_tracking = true;
            if (GetCapture() != this) SetCapture();
            NotifyDown();
        }
    }

    afx_msg void OnLButtonUp(UINT nFlags, CPoint point)
    {
        NotifyUp();
        CButton::OnLButtonUp(nFlags, point);
    }

    afx_msg void OnCaptureChanged(CWnd* pWnd)
    {
        NotifyUp();
        CButton::OnCaptureChanged(pWnd);
    }

    afx_msg void OnCancelMode()
    {
        NotifyUp();
        CButton::OnCancelMode();
    }

    DECLARE_MESSAGE_MAP()
};
