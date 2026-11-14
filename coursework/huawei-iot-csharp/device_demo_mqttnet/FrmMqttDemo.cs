using device_demo_mqttnet.Utility;
using MQTTnet;
using MQTTnet.Client.Connecting;
using MQTTnet.Client.Disconnecting;
using MQTTnet.Client.Options;
using MQTTnet.Client.Receiving;
using MQTTnet.Extensions.ManagedClient;
using MQTTnet.Formatter;
using MQTTnet.Protocol;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Drawing;
using System.IO.Ports;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace device_demo_mqttnet
{
    public partial class FrmMqttDemo : Form
    {
        private static IManagedMqttClient client = null;

        private static IManagedMqttClientOptions options = null;

        private static readonly ushort DEFAULT_KEEPLIVE = 120;

        private static readonly ushort RECONNECT_TIME = 60000;

        private static readonly ushort DEFAULT_CONNECT_TIMEOUT = 1;

        private long minBackoff = 1000;

        private long maxBackoff = 30 * 1000;

        private long defaultBackoff = 1000;

        private static int retryTimes = 0;

        Random random = new Random();
        private SerialPort comm = new SerialPort();//我加的，新建一个串口变量
        private StringBuilder builder = new StringBuilder();//避免在事件处理方法中反复的创建，定义到外面。

        public FrmMqttDemo()
        {
            InitializeComponent();

            SetDefaultProperty();//设置界面的默认值
            BindQosData();//选择Qos(0,1)
        }

        private void SetDefaultProperty()
        {
            txtServerUri.Text = ConfigurationManager.AppSettings["serverUri"];
            txtDeviceId.Text = ConfigurationManager.AppSettings["deviceId"];
            txtDeviceSecret.Text = ConfigurationManager.AppSettings["deviceSecret"];

            txtSubTopic.Text = string.Format("$oc/devices/{0}/sys/commands/#", txtDeviceId.Text);

            txtPubTopic.Text = string.Format("$oc/devices/{0}/sys/properties/report",txtDeviceId.Text);
        }

        private void BindQosData()
        {
            Dictionary<string, int> kvDictonary = new Dictionary<string, int>();
            kvDictonary.Add("0", 0);
            kvDictonary.Add("1", 1);

            BindingSource bs = new BindingSource();
            bs.DataSource = kvDictonary;
            cbOosSelect.DataSource = bs;
            cbOosSelect.ValueMember = "Value";
            cbOosSelect.DisplayMember = "Key";
        }

        private void btnConnect_Click(object sender, EventArgs e)
        {
            Task.Run(async () => { await ConnectMqttServerAsync(); });
        }

        private void btnDisconnect_Click(object sender, EventArgs e)
        {
            minBackoff = 1000;

            maxBackoff = 30 * 1000;

            defaultBackoff = 1000;

            retryTimes = 0;

            Task.Run(async () => { await DisconnectMqttServerAsync(); });
        }

        private async Task DisconnectMqttServerAsync()
        {
            //断开连接
            await client.StopAsync();
        }

        /// <summary>
        /// 连接服务器
        /// </summary>
        /// <returns></returns>
        private async Task ConnectMqttServerAsync()
        {
            try
            {
                int portIsSsl = int.Parse(ConfigurationManager.AppSettings["portIsSsl"]);
                int portNotSsl = int.Parse(ConfigurationManager.AppSettings["portNotSsl"]);

                if (client == null)
                {
                    client = new MqttFactory().CreateManagedMqttClient();
                }

                string timestamp = DateTime.Now.ToString("yyyyMMddHH");
                string clientID = txtDeviceId.Text + "_0_0_" + timestamp;

                // 对密码进行HmacSHA256加密
                string secret = string.Empty;
                if (!string.IsNullOrEmpty(txtDeviceSecret.Text))
                {
                    secret = EncryptUtil.HmacSHA256(txtDeviceSecret.Text, timestamp);
                }

                // 判断是否为安全连接
                if (!cbSSLConnect.Checked)
                {
                    options = new ManagedMqttClientOptionsBuilder()
                    .WithAutoReconnectDelay(TimeSpan.FromSeconds(RECONNECT_TIME))
                    .WithClientOptions(new MqttClientOptionsBuilder()
                        .WithTcpServer(txtServerUri.Text, portNotSsl)
                        .WithCommunicationTimeout(TimeSpan.FromSeconds(DEFAULT_CONNECT_TIMEOUT))
                        .WithCredentials(txtDeviceId.Text, secret)
                        .WithClientId(clientID)
                        .WithKeepAlivePeriod(TimeSpan.FromSeconds(DEFAULT_KEEPLIVE))
                        .WithCleanSession(false)
                        .WithProtocolVersion(MqttProtocolVersion.V311)
                        .Build())
                    .Build();
                }
                else
                {
                    string caCertPath = Environment.CurrentDirectory + @"\certificate\rootcert.pem";
                    X509Certificate2 crt = new X509Certificate2(caCertPath);

                    options = new ManagedMqttClientOptionsBuilder()
                    .WithAutoReconnectDelay(TimeSpan.FromSeconds(RECONNECT_TIME))
                    .WithClientOptions(new MqttClientOptionsBuilder()
                        .WithTcpServer(txtServerUri.Text, portIsSsl)
                        .WithCommunicationTimeout(TimeSpan.FromSeconds(DEFAULT_CONNECT_TIMEOUT))
                        .WithCredentials(txtDeviceId.Text, secret)
                        .WithClientId(clientID)
                        .WithKeepAlivePeriod(TimeSpan.FromSeconds(DEFAULT_KEEPLIVE))
                        .WithCleanSession(false)
                        .WithTls(new MqttClientOptionsBuilderTlsParameters()
                        {
                            AllowUntrustedCertificates = true,
                            UseTls = true,
                            Certificates = new List<X509Certificate> { crt },
                            CertificateValidationHandler = delegate { return true; },
                            IgnoreCertificateChainErrors = false,
                            IgnoreCertificateRevocationErrors = false
                        })
                        .WithProtocolVersion(MqttProtocolVersion.V311)
                        .Build())
                    .Build();
                }

                Invoke((new Action(() =>
                {
                    ShowLogs($"{"try to connect to server " + txtServerUri.Text}{Environment.NewLine}");
                })));

                if (client.IsStarted)
                {
                    await client.StopAsync();
                }

                // 注册事件
                client.ApplicationMessageProcessedHandler = new ApplicationMessageProcessedHandlerDelegate(new Action<ApplicationMessageProcessedEventArgs>(ApplicationMessageProcessedHandlerMethod)); // 消息发布回调

                client.ApplicationMessageReceivedHandler = new MqttApplicationMessageReceivedHandlerDelegate(new Action<MqttApplicationMessageReceivedEventArgs>(MqttApplicationMessageReceived)); // 命令下发回调

                client.ConnectedHandler = new MqttClientConnectedHandlerDelegate(new Action<MqttClientConnectedEventArgs>(OnMqttClientConnected)); // 连接成功回调

                client.DisconnectedHandler = new MqttClientDisconnectedHandlerDelegate(new Action<MqttClientDisconnectedEventArgs>(OnMqttClientDisconnected)); // 连接断开回调

                // 连接平台设备
                await client.StartAsync(options);

            }
            catch (Exception ex)
            {
                Invoke((new Action(() =>
                {
                    ShowLogs($"connect to mqtt server fail" + Environment.NewLine);
                })));
            }
        }

        /// <summary>
        /// 接收到消息
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void MqttApplicationMessageReceived(MqttApplicationMessageReceivedEventArgs e)
        {
            Invoke((new Action(() =>
            {
                ShowLogs($"received message is {Encoding.UTF8.GetString(e.ApplicationMessage.Payload)}{Environment.NewLine}");

                if (Encoding.UTF8.GetString(e.ApplicationMessage.Payload).Contains("\"ON\""))
                {
                    buttonOpenLight_Click(null, null);
                    ShowLogs($"Open command is success!{Environment.NewLine}");
                }

                if (Encoding.UTF8.GetString(e.ApplicationMessage.Payload).Contains("\"OFF\""))
                {
                    buttonCloseLight_Click(null, null);
                    ShowLogs($"Close command is success!{Environment.NewLine}");
                }

                string msg = "{\"result_code\": 0,\"response_name\": \"COMMAND_RESPONSE\",\"paras\": {\"result\": \"success\"}}";

                string topic = "$oc/devices/" + txtDeviceId.Text + "/sys/commands/response/request_id=" + e.ApplicationMessage.Topic.Split('=')[1];

                ShowLogs($"{"response message msg = " + msg}{Environment.NewLine}");
                
                var appMsg = new MqttApplicationMessage();
                appMsg.Payload = Encoding.UTF8.GetBytes(msg);
                appMsg.Topic = topic;
                appMsg.QualityOfServiceLevel = int.Parse(cbOosSelect.SelectedValue.ToString()) == 0 ? MqttQualityOfServiceLevel.AtMostOnce : MqttQualityOfServiceLevel.AtLeastOnce;
                appMsg.Retain = false;

                // 上行响应
                client.PublishAsync(appMsg).Wait();
            })));
        }

        /// <summary>
        /// 消息发布回调
        /// </summary>
        /// <param name="e"></param>
        private void ApplicationMessageProcessedHandlerMethod(ApplicationMessageProcessedEventArgs e)
        {
            try
            {
                if (e.HasFailed)
                {
                    Invoke((new Action(() =>
                    {
                        ShowLogs("publish messageId is " + e.ApplicationMessage.Id + ", topic: " + e.ApplicationMessage.ApplicationMessage.Topic + ", payload: " + Encoding.UTF8.GetString(e.ApplicationMessage.ApplicationMessage.Payload) + " is published fail");
                    })));
                }
                else if (e.HasSucceeded)
                {
                    Invoke((new Action(() =>
                    {
                        ShowLogs("publish messageId " + e.ApplicationMessage.Id + ", topic: " + e.ApplicationMessage.ApplicationMessage.Topic + ", payload: " + Encoding.UTF8.GetString(e.ApplicationMessage.ApplicationMessage.Payload) + " is published success");
                    })));
                }
            }
            catch (Exception ex)
            {
                Invoke((new Action(() =>
                {
                    ShowLogs("mqtt demo message publish error: " + ex.Message + Environment.NewLine);
                })));
            }
        }

        /// <summary>
        /// 服务器连接成功
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void OnMqttClientConnected(MqttClientConnectedEventArgs e)
        {
            Invoke((new Action(() =>
            {
                ShowLogs("connect to mqtt server success, deviceId is " + txtDeviceId.Text + Environment.NewLine);

                btnConnect.Enabled = false;
                btnDisconnect.Enabled = true;
                btnPublish.Enabled = true;
                btnSubscribe.Enabled = true;
            })));
        }

        /// <summary>
        /// 断开服务器连接
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void OnMqttClientDisconnected(MqttClientDisconnectedEventArgs e)
        {
            try {
                Invoke((new Action(() =>
                {
                    ShowLogs("mqtt server is disconnected" + Environment.NewLine);

                    txtSubTopic.Enabled = true;
                    btnConnect.Enabled = true;
                    btnDisconnect.Enabled = false;
                    btnPublish.Enabled = false;
                    btnSubscribe.Enabled = false;
                })));
                
                if (cbReconnect.Checked)
                {
                    Invoke((new Action(() =>
                    {
                        ShowLogs("reconnect is starting" + Environment.NewLine);
                    })));

                    //退避重连
                    int lowBound = (int)(defaultBackoff * 0.8);
                    int highBound = (int)(defaultBackoff * 1.2);
                    long randomBackOff = random.Next(highBound - lowBound);
                    long backOffWithJitter = (int)(Math.Pow(2.0, retryTimes)) * (randomBackOff + lowBound);
                    long waitTImeUtilNextRetry = (int)(minBackoff + backOffWithJitter) > maxBackoff ? maxBackoff : (minBackoff + backOffWithJitter);

                    Invoke((new Action(() =>
                    {
                        ShowLogs("next retry time: " + waitTImeUtilNextRetry + Environment.NewLine);
                    })));

                    Thread.Sleep((int)waitTImeUtilNextRetry);

                    retryTimes++;

                    Task.Run(async () => { await ConnectMqttServerAsync(); });
                }
            }
            catch (Exception ex)
            {
                Invoke((new Action(() =>
                {
                    ShowLogs("mqtt demo error: " + ex.Message + Environment.NewLine);
                })));
            }
        }

        private void btnPublish_Click(object sender, EventArgs e)
        {
            Invoke((new Action(() =>
            {
                string topic = txtPubTopic.Text.Trim();

                ShowLogs("publish message topic = " + topic + Environment.NewLine);

                if (string.IsNullOrEmpty(topic))
                {
                    MessageBox.Show("发布主题不能为空");
                    return;
                }

                string inputString = txtSendMessage.Text.Trim();
                
                var appMsg = new MqttApplicationMessage();
                appMsg.Payload = Encoding.UTF8.GetBytes(inputString);
                appMsg.Topic = topic;
                appMsg.QualityOfServiceLevel = int.Parse(cbOosSelect.SelectedValue.ToString()) == 0 ? MqttQualityOfServiceLevel.AtMostOnce : MqttQualityOfServiceLevel.AtLeastOnce;
                appMsg.Retain = false;

                // 上行响应
                client.PublishAsync(appMsg).Wait();
            })));
        }

        private void btnSubscribe_Click(object sender, EventArgs e)
        {
            string topic = txtSubTopic.Text.Trim();

            if (string.IsNullOrEmpty(topic))
            {
                MessageBox.Show("订阅主题不能为空！");
                return;
            }

            if (!client.IsConnected)
            {
                MessageBox.Show("MQTT客户端尚未连接！");
                return;
            }
            
            List<MqttTopicFilter> listTopic = new List<MqttTopicFilter>();

            var topicFilterBulderPreTopic = new MqttTopicFilterBuilder().WithTopic(topic).Build();
            listTopic.Add(topicFilterBulderPreTopic);

            // 订阅Topic
            client.SubscribeAsync(listTopic.ToArray()).Wait();

            ShowLogs($"topic : [{topic}] is subscribe success" + Environment.NewLine);
            
            txtSubTopic.Enabled = false;
            btnSubscribe.Enabled = false;
        }

        private void txtDeviceId_TextChanged(object sender, EventArgs e)
        {
            //更改deviceID后订阅Topic和发布Topic对应的deviceID同时改变
            Regex r = new Regex("(?<=/devices/).*?(?=/sys/)", RegexOptions.IgnoreCase);

            txtSubTopic.Text = r.Replace(txtSubTopic.Text, txtDeviceId.Text);
            txtPubTopic.Text = r.Replace(txtPubTopic.Text, txtDeviceId.Text);
        }

        private void ShowLogs(string msg)
        {
            txtReceiveMessage.AppendText(string.Format("{0} - {1}",DateTime.Now.ToString("yyyy-MM-dd hh:mm:ss"),msg));
        }

        private void linkLabel1_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            txtReceiveMessage.Clear();//清空日志
        }

        private void cbReconnect_Click(object sender, EventArgs e)
        {
            if (cbReconnect.Checked && (client == null || !client.IsConnected))
            {
                Task.Run(async () => { await ConnectMqttServerAsync(); });
            }
            else
            {
                minBackoff = 1000;

                maxBackoff = 30 * 1000;

                defaultBackoff = 1000;

                retryTimes = 0;
            }
        }

        void comm_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            int n = comm.BytesToRead;
            byte[] buf = new byte[n];
            comm.Read(buf, 0, n);
            builder.Clear();

            this.Invoke((EventHandler)(delegate
            {
                // 解析温湿度值
                string wendu = (buf[4] - 48).ToString() + (buf[5] - 48).ToString();
                string shidu = (buf[8] - 48).ToString() + (buf[9] - 48).ToString();

                // 更新界面显示
                this.WenDuZhi.Text = wendu;
                this.ShiDuZhi.Text = shidu;

                // 温度报警逻辑
                if (Convert.ToInt32(wendu) > 20)
                {
                    //DaoZeiBaoJing.BackColor = Color.Red;
                    // axWindowsMediaPlayer1.URL = @"E:\download\warning.mp3";
                }
                else
                {
                    //DaoZeiBaoJing.BackColor = Color.GreenYellow;
                }

                if (client != null && client.IsConnected)
                {
                    string reportMsg = "{\"services\":[{\"service_id\":\"Temperature\",\"properties\":{\"temperature\":"
                        + wendu + ",\"humidity\":" + shidu + "}}]}";

                    string topic = txtPubTopic.Text.Trim();

                    var appMsg = new MqttApplicationMessage();
                    appMsg.Payload = Encoding.UTF8.GetBytes(reportMsg);
                    appMsg.Topic = topic;
                    appMsg.QualityOfServiceLevel = MqttQualityOfServiceLevel.AtLeastOnce;
                    appMsg.Retain = false;

                    client.PublishAsync(appMsg);

                    ShowLogs($"自动上报温湿度 - 温度:{wendu}°C, 湿度:{shidu}% {Environment.NewLine}");
                }
            }));
        }
        private void FrmMqttDemo_Load(object sender, EventArgs e)
        {
            MultiLanguage.SetDefaultLanguage(ConfigurationManager.AppSettings["language"]);
            //load language
            MultiLanguage.LoadLanguage(this, typeof(FrmMqttDemo));

            string[] ports = SerialPort.GetPortNames();
            Array.Sort(ports);
            comboPortName.Items.AddRange(ports);
            comboPortName.SelectedIndex = comboPortName.Items.Count > 0 ? 0 : -1;

            //初始化SerialPort对象  
            comm.NewLine = "/r/n";
            comm.RtsEnable = true;//根据实际情况吧。 
            comm.DataReceived += comm_DataReceived;
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
            buttonOpenCloseCom.Text = comm.IsOpen ? "关闭串口" : "打开串口";
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

        private void comboPortName_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void WenDuZhi_TextChanged(object sender, EventArgs e)
        {

        }

        private void ShiDuZhi_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
