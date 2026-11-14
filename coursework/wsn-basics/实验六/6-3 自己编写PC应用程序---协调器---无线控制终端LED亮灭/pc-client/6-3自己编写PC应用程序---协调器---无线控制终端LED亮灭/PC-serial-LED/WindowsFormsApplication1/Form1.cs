using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
//以上几句是自动生成的

using System.IO.Ports;//我加的，包含串口相关的
using System.Text.RegularExpressions;//我加的


namespace WindowsFormsApplication1
{
    public partial class PCZigbeeLed : Form
    {
        private SerialPort comm = new SerialPort();//我加的，新建一个串口变量
        private bool closing = false;//是否正在关闭串口，执行Application.DoEvents，并阻止再次invoke
        private bool Listening = false;//是否没有执行完invoke相关操作
        public PCZigbeeLed()//自动生成的函数
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            string[] ports = SerialPort.GetPortNames();
            Array.Sort(ports);
            comboPortName.Items.AddRange(ports);
            comboPortName.SelectedIndex = comboPortName.Items.Count > 0 ? 0 : -1;

            //初始化SerialPort对象  
            comm.NewLine = "/r/n";
            comm.RtsEnable = true;//根据实际情况吧。 
            //comm.DataReceived += comm_DataReceived;
        }

    private void comboPortName_SelectedIndexChanged(object sender, EventArgs e)
    {

     }

        private void buttonOpenClosecom_Click(object sender, EventArgs e)
        {
            //根据当前串口对象，来判断操作  
            if (comm.IsOpen)
            {
                closing = true;
                while (Listening) Application.DoEvents();
                //打开时点击，则关闭串口  
                comm.Close();
                //this.timer1.Stop();
                closing = false;
            }
            else
            {
                //关闭时点击，则设置好端口，波特率后打开  
                comm.PortName = comboPortName.Text;
                comm.BaudRate = 9600;
                try
                {
                    comm.Open();
                }
                catch (Exception ex)
                {
                    //捕获到异常信息，创建一个新的comm对象，之前的不能用了。  
                    comm = new SerialPort();
                    //现实异常信息给客户。  
                    MessageBox.Show(ex.Message); 
                }
            }
            //设置按钮的状态  
            buttonOpenClosecom.Text = comm.IsOpen ? "关闭串口" : "打开串口";
        }

        private void buttonOpenLight_Click(object sender, EventArgs e)
        {
            byte[] SendBuf = new byte[2];
            SendBuf[0] = 0x32;
            SendBuf[1] = 0x31;
            comm.Write(SendBuf, 0, 2);
            System.Threading.Thread.Sleep(100);
        }

        private void buttonCloseLight_Click(object sender, EventArgs e)
        {
            byte[] SendBuf = new byte[2];
            SendBuf[0] = 0x32;
            SendBuf[1] = 0x30;
            comm.Write(SendBuf, 0, 2);
            System.Threading.Thread.Sleep(100);
        }
    }
}
