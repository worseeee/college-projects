
// MFCBasicCalculatorDlg.cpp: 实现文件
//

#include "pch.h"
#include "framework.h"
#include "MFCBasicCalculator.h"
#include "MFCBasicCalculatorDlg.h"
#include "afxdialogex.h"
#include "resource.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// 用于应用程序“关于”菜单项的 CAboutDlg 对话框

class CAboutDlg : public CDialogEx
{
public:
	CAboutDlg();

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_ABOUTBOX };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

// 实现
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(IDD_ABOUTBOX)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()

// 统一格式化计算结果，去掉小数末尾多余的 0
static CString FormatResult(double value)
{
	CString str;

	// 先保留 6 位小数
	str.Format(_T("%.6f"), value);

	// 去掉小数末尾多余的 0
	str.TrimRight(_T('0'));

	// 如果小数点变成最后一个字符，也将其去掉
	str.TrimRight(_T('.'));

	// 避免出现空字符串或 -0
	if (str.IsEmpty() || str == _T("-0"))
	{
		str = _T("0");
	}

	return str;
}

// CMFCBasicCalculatorDlg 对话框



CMFCBasicCalculatorDlg::CMFCBasicCalculatorDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_MFCBASICCALCULATOR_DIALOG, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CMFCBasicCalculatorDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CMFCBasicCalculatorDlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_BUTTON_ADD, &CMFCBasicCalculatorDlg::OnBnClickedButtonAdd)
	ON_BN_CLICKED(IDC_BUTTON_SUB, &CMFCBasicCalculatorDlg::OnBnClickedButtonSub)
	ON_BN_CLICKED(IDC_BUTTON_MUL, &CMFCBasicCalculatorDlg::OnBnClickedButtonMul)
	ON_BN_CLICKED(IDC_BUTTON_DIV, &CMFCBasicCalculatorDlg::OnBnClickedButtonDiv)
	ON_BN_CLICKED(IDC_BUTTON_CLEAR, &CMFCBasicCalculatorDlg::OnBnClickedButtonClear)
END_MESSAGE_MAP()


// CMFCBasicCalculatorDlg 消息处理程序

BOOL CMFCBasicCalculatorDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// 将“关于...”菜单项添加到系统菜单中。

	// IDM_ABOUTBOX 必须在系统命令范围内。
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != nullptr)
	{
		BOOL bNameValid;
		CString strAboutMenu;
		bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
		ASSERT(bNameValid);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// 设置此对话框的图标。  当应用程序主窗口不是对话框时，框架将自动
	//  执行此操作
	SetIcon(m_hIcon, TRUE);			// 设置大图标
	SetIcon(m_hIcon, FALSE);		// 设置小图标

	// TODO: 在此添加额外的初始化代码

	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
}

void CMFCBasicCalculatorDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialogEx::OnSysCommand(nID, lParam);
	}
}

// 如果向对话框添加最小化按钮，则需要下面的代码
//  来绘制该图标。  对于使用文档/视图模型的 MFC 应用程序，
//  这将由框架自动完成。

void CMFCBasicCalculatorDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // 用于绘制的设备上下文

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 使图标在工作区矩形中居中
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 绘制图标
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

//当用户拖动最小化窗口时系统调用此函数取得光标
//显示。
HCURSOR CMFCBasicCalculatorDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}

void CMFCBasicCalculatorDlg::OnBnClickedButtonAdd()
{
	CString str1, str2, str3;

	GetDlgItemText(IDC_EDIT1, str1);
	GetDlgItemText(IDC_EDIT2, str2);

	double a = _ttof(str1);
	double b = _ttof(str2);

	double result = a + b;

	str3 = FormatResult(result);

	SetDlgItemText(IDC_EDIT3, str3);
}

void CMFCBasicCalculatorDlg::OnBnClickedButtonSub()
{
	CString str1, str2, str3;

	GetDlgItemText(IDC_EDIT1, str1);
	GetDlgItemText(IDC_EDIT2, str2);

	double a = _ttof(str1);
	double b = _ttof(str2);

	double result = a - b;

	str3 = FormatResult(result);

	SetDlgItemText(IDC_EDIT3, str3);
}

void CMFCBasicCalculatorDlg::OnBnClickedButtonMul()
{
	CString str1, str2, str3;

	GetDlgItemText(IDC_EDIT1, str1);
	GetDlgItemText(IDC_EDIT2, str2);

	double a = _ttof(str1);
	double b = _ttof(str2);

	double result = a * b;

	str3 = FormatResult(result);

	SetDlgItemText(IDC_EDIT3, str3);
}

void CMFCBasicCalculatorDlg::OnBnClickedButtonDiv()
{
	CString str1, str2, str3;

	GetDlgItemText(IDC_EDIT1, str1);
	GetDlgItemText(IDC_EDIT2, str2);

	double a = _ttof(str1);
	double b = _ttof(str2);

	if (b == 0.0)
	{
		AfxMessageBox(_T("除数不能为零！"));
		return;
	}

	double result = a / b;

	str3 = FormatResult(result);

	SetDlgItemText(IDC_EDIT3, str3);
}

void CMFCBasicCalculatorDlg::OnBnClickedButtonClear()
{
	SetDlgItemText(IDC_EDIT1, _T(""));
	SetDlgItemText(IDC_EDIT2, _T(""));
	SetDlgItemText(IDC_EDIT3, _T(""));
}
