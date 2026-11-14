using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
//以上几句是自动生成的

using System.IO.Ports;//我加的，包含串口相关的
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;//我加的
using System.Threading.Tasks;
using System.Windows.Forms;


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
            comm.DataReceived += comm_DataReceived;
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
            SendBuf[0] = 0x31;
            SendBuf[1] = 0x31;
            comm.Write(SendBuf, 0, 2);//向串口发送两个字符21，
            System.Threading.Thread.Sleep(100);
        }

        private void buttonCloseLight_Click(object sender, EventArgs e)
        {
            byte[] SendBuf = new byte[2];
            SendBuf[0] = 0x31;
            SendBuf[1] = 0x30;
            comm.Write(SendBuf, 0, 2);//向串口发送两个字符20，
            System.Threading.Thread.Sleep(100);
        }

        void comm_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            int n = comm.BytesToRead;//先记录下来，避免某种原因，人为的原因，操作几次之间时间长，缓存不一致
            byte[] buf = new byte[n];//声明一个临时数组存储当前来的串口数据
            comm.Read(buf, 0, n);//读取缓冲数据
            //因为要访问ui资源，所以需要使用invoke方式同步ui。
            this.Invoke((EventHandler)(delegate
            {
                if (buf[0] == 0x38)
                    textBox1.Text = "开继电器命令执行成功！";
                if (buf[0] == 0x39)
                    textBox1.Text = "关继电器命令执行成功！";
            }));
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
