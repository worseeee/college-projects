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


                this.WenDuZhi.Text = (buf[0] - 48).ToString() + (buf[1] - 48).ToString();
                if (Convert.ToInt32(this.WenDuZhi.Text) > 50)//如果串口接收到0，
                {
                    DaoZeiBaoJing.BackColor = Color.Red;//就变为红色
                    axWindowsMediaPlayer1.URL = @"E:\download\warning.mp3";
                }
                else//否则有人在人体红外传感器周围活动
                {
                    DaoZeiBaoJing.BackColor = Color.GreenYellow;//则保持绿色不变
                }
            }));
        }

        private void WenDuZhi_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
