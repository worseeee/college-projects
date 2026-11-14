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


namespace tempsensor
{
    public partial class Form1 : Form
    {
        private SerialPort comm = new SerialPort();//我加的，新建一个串口变量
        private StringBuilder builder = new StringBuilder();//避免在事件处理方法中反复的创建，定义到外面。  
        private int mode = 0;//0手动，1自动
        public Form1()
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

        private void buttonOpenCloseCom_Click(object sender, EventArgs e)
        {
            //根据当前串口对象，来判断操作  
            if (comm.IsOpen)
            {
                comm.Close();
            }
            else
            {
                //关闭时点击，则设置好端口，波特率后打开  
                comm.PortName = comboPortName.Text;
                comm.BaudRate = 115200;
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
            buttonOpenCloseCom.Text = comm.IsOpen ? "关闭串口" : "打开串口";
        }

        void comm_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            int n = comm.BytesToRead;//先记录下来，避免某种原因，人为的原因，操作几次之间时间长，缓存不一致
            byte[] buf = new byte[n];//声明一个临时数组存储当前来的串口数据
            comm.Read(buf, 0, n);//读取缓冲数据
            builder.Clear();//清除字符串构造器的内容
            //因为要访问ui资源，所以需要使用invoke方式同步ui。
            this.Invoke((EventHandler)(delegate
            {

                    
                //直接按ASCII规则转换成字符串    
                //builder.Append(Encoding.ASCII.GetString(buf));
                
                //追加的形式添加到文本框末端，并滚动到最后。
                this.WenDuZhi.Text=(buf[0]-48).ToString() + (buf[1] - 48).ToString();
                if(mode==1)
                {
                    if (Convert.ToInt32(WenDuZhi.Text) > Convert.ToInt32(textBoxThreshhold.Text))
                    {
                        buttonOpenLight_click(null, null);
                        byte[] SendBuf = new byte[2];
                        SendBuf[0] = 0x32;
                        SendBuf[1] = 0x32;
                        comm.Write(SendBuf, 0, 2);
                    }
                    else
                    {
                        buttonCloseLight_Click(null, null);
                        byte[] SendBuf = new byte[2];
                        SendBuf[0] = 0x32;
                        SendBuf[1] = 0x33;
                        comm.Write(SendBuf, 0, 2);
                    }
                }

            }));
        }

        private void WenDuZhi_TextChanged(object sender, EventArgs e)
        {

        }

        private void buttonCloseLight_Click(object sender, EventArgs e)
        {
            byte[] SendBuf = new byte[2];
            SendBuf[0] = 0x32;
            SendBuf[1] = 0x30;
            comm.Write(SendBuf, 0, 2);
            System.Threading.Thread.Sleep(100);
        }

        private void buttonOpenLight_click(object sender, EventArgs e)
        {
            byte[] SendBuf = new byte[2];
            SendBuf[0] = 0x32;
            SendBuf[1] = 0x31;
            comm.Write(SendBuf, 0, 2);
            System.Threading.Thread.Sleep(100);
        }

        private void WenDuZhi_TextChanged_1(object sender, EventArgs e)
        {

        }

        private void buttonMode_Click(object sender, EventArgs e)
        {
            if (mode == 0)
                mode = 1;
            else
                mode = 0;
        }
    }
}
