namespace device_demo_mqttnet
{
    partial class FrmMqttDemo
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.btnSubscribe = new System.Windows.Forms.Button();
            this.btnPublish = new System.Windows.Forms.Button();
            this.txtSendMessage = new System.Windows.Forms.TextBox();
            this.txtPubTopic = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.txtReceiveMessage = new System.Windows.Forms.TextBox();
            this.txtSubTopic = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.cbSSLConnect = new System.Windows.Forms.CheckBox();
            this.label4 = new System.Windows.Forms.Label();
            this.cbOosSelect = new System.Windows.Forms.ComboBox();
            this.btnDisconnect = new System.Windows.Forms.Button();
            this.btnConnect = new System.Windows.Forms.Button();
            this.label5 = new System.Windows.Forms.Label();
            this.txtServerUri = new System.Windows.Forms.TextBox();
            this.label6 = new System.Windows.Forms.Label();
            this.txtDeviceId = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.txtDeviceSecret = new System.Windows.Forms.TextBox();
            this.label7 = new System.Windows.Forms.Label();
            this.linkLabel1 = new System.Windows.Forms.LinkLabel();
            this.cbReconnect = new System.Windows.Forms.CheckBox();
            this.comcaozuo = new System.Windows.Forms.GroupBox();
            this.XuanZeChuanKou = new System.Windows.Forms.Label();
            this.comboPortName = new System.Windows.Forms.ComboBox();
            this.buttonOpenCloseCom = new System.Windows.Forms.Button();
            this.WenShiDuShuju = new System.Windows.Forms.GroupBox();
            this.label_shidu = new System.Windows.Forms.Label();
            this.label_wenduzhi = new System.Windows.Forms.Label();
            this.ShiDuZhi = new System.Windows.Forms.TextBox();
            this.WenDuZhi = new System.Windows.Forms.TextBox();
            this.comcaozuo.SuspendLayout();
            this.WenShiDuShuju.SuspendLayout();
            this.SuspendLayout();
            // 
            // btnSubscribe
            // 
            this.btnSubscribe.Enabled = false;
            this.btnSubscribe.Location = new System.Drawing.Point(1143, 144);
            this.btnSubscribe.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.btnSubscribe.Name = "btnSubscribe";
            this.btnSubscribe.Size = new System.Drawing.Size(131, 35);
            this.btnSubscribe.TabIndex = 23;
            this.btnSubscribe.Text = "订阅";
            this.btnSubscribe.UseVisualStyleBackColor = true;
            this.btnSubscribe.Click += new System.EventHandler(this.btnSubscribe_Click);
            // 
            // btnPublish
            // 
            this.btnPublish.Enabled = false;
            this.btnPublish.Location = new System.Drawing.Point(532, 723);
            this.btnPublish.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.btnPublish.Name = "btnPublish";
            this.btnPublish.Size = new System.Drawing.Size(143, 54);
            this.btnPublish.TabIndex = 22;
            this.btnPublish.Text = "发布";
            this.btnPublish.UseVisualStyleBackColor = true;
            this.btnPublish.Click += new System.EventHandler(this.btnPublish_Click);
            // 
            // txtSendMessage
            // 
            this.txtSendMessage.Location = new System.Drawing.Point(18, 572);
            this.txtSendMessage.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.txtSendMessage.Multiline = true;
            this.txtSendMessage.Name = "txtSendMessage";
            this.txtSendMessage.Size = new System.Drawing.Size(1256, 130);
            this.txtSendMessage.TabIndex = 21;
            this.txtSendMessage.Text = "{\"services\":[{\"properties\":{\"alarm\":1,\"temperature\":92.670784,\"humidity\":78.37673" +
    ",\"smokeConcentration\":19.97906},\"service_id\":\"smokeDetector\",\"event_time\":null}]" +
    "}";
            // 
            // txtPubTopic
            // 
            this.txtPubTopic.Location = new System.Drawing.Point(185, 518);
            this.txtPubTopic.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.txtPubTopic.Name = "txtPubTopic";
            this.txtPubTopic.Size = new System.Drawing.Size(1089, 28);
            this.txtPubTopic.TabIndex = 20;
            // 
            // label2
            // 
            this.label2.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.label2.Location = new System.Drawing.Point(21, 522);
            this.label2.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(156, 18);
            this.label2.TabIndex = 19;
            this.label2.Text = "发布Topic";
            this.label2.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // txtReceiveMessage
            // 
            this.txtReceiveMessage.Location = new System.Drawing.Point(18, 221);
            this.txtReceiveMessage.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.txtReceiveMessage.Multiline = true;
            this.txtReceiveMessage.Name = "txtReceiveMessage";
            this.txtReceiveMessage.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtReceiveMessage.Size = new System.Drawing.Size(1256, 268);
            this.txtReceiveMessage.TabIndex = 18;
            // 
            // txtSubTopic
            // 
            this.txtSubTopic.Location = new System.Drawing.Point(185, 145);
            this.txtSubTopic.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.txtSubTopic.Name = "txtSubTopic";
            this.txtSubTopic.Size = new System.Drawing.Size(950, 28);
            this.txtSubTopic.TabIndex = 17;
            // 
            // label1
            // 
            this.label1.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.label1.Location = new System.Drawing.Point(-12, 150);
            this.label1.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(189, 18);
            this.label1.TabIndex = 16;
            this.label1.Text = "订阅Topic";
            this.label1.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // cbSSLConnect
            // 
            this.cbSSLConnect.AutoSize = true;
            this.cbSSLConnect.Location = new System.Drawing.Point(69, 32);
            this.cbSSLConnect.Margin = new System.Windows.Forms.Padding(3, 4, 3, 4);
            this.cbSSLConnect.Name = "cbSSLConnect";
            this.cbSSLConnect.Size = new System.Drawing.Size(151, 22);
            this.cbSSLConnect.TabIndex = 27;
            this.cbSSLConnect.Text = "是否为SSL连接";
            this.cbSSLConnect.UseVisualStyleBackColor = true;
            // 
            // label4
            // 
            this.label4.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.label4.Location = new System.Drawing.Point(505, 33);
            this.label4.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(69, 18);
            this.label4.TabIndex = 28;
            this.label4.Text = "QoS";
            this.label4.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // cbOosSelect
            // 
            this.cbOosSelect.DisplayMember = "0,1";
            this.cbOosSelect.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cbOosSelect.FormattingEnabled = true;
            this.cbOosSelect.Location = new System.Drawing.Point(581, 29);
            this.cbOosSelect.Margin = new System.Windows.Forms.Padding(3, 4, 3, 4);
            this.cbOosSelect.Name = "cbOosSelect";
            this.cbOosSelect.Size = new System.Drawing.Size(158, 26);
            this.cbOosSelect.TabIndex = 29;
            // 
            // btnDisconnect
            // 
            this.btnDisconnect.Enabled = false;
            this.btnDisconnect.Location = new System.Drawing.Point(1011, 24);
            this.btnDisconnect.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.btnDisconnect.Name = "btnDisconnect";
            this.btnDisconnect.Size = new System.Drawing.Size(124, 35);
            this.btnDisconnect.TabIndex = 30;
            this.btnDisconnect.Text = "断开连接";
            this.btnDisconnect.UseVisualStyleBackColor = true;
            this.btnDisconnect.Click += new System.EventHandler(this.btnDisconnect_Click);
            // 
            // btnConnect
            // 
            this.btnConnect.Location = new System.Drawing.Point(825, 24);
            this.btnConnect.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.btnConnect.Name = "btnConnect";
            this.btnConnect.Size = new System.Drawing.Size(124, 35);
            this.btnConnect.TabIndex = 31;
            this.btnConnect.Text = "新建连接";
            this.btnConnect.UseVisualStyleBackColor = true;
            this.btnConnect.Click += new System.EventHandler(this.btnConnect_Click);
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(15, 198);
            this.label5.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(62, 18);
            this.label5.TabIndex = 32;
            this.label5.Text = "日志：";
            // 
            // txtServerUri
            // 
            this.txtServerUri.Location = new System.Drawing.Point(185, 86);
            this.txtServerUri.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.txtServerUri.Name = "txtServerUri";
            this.txtServerUri.Size = new System.Drawing.Size(285, 28);
            this.txtServerUri.TabIndex = 34;
            // 
            // label6
            // 
            this.label6.Location = new System.Drawing.Point(15, 91);
            this.label6.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(162, 18);
            this.label6.TabIndex = 33;
            this.label6.Text = "Server地址";
            this.label6.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // txtDeviceId
            // 
            this.txtDeviceId.Location = new System.Drawing.Point(581, 84);
            this.txtDeviceId.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.txtDeviceId.Name = "txtDeviceId";
            this.txtDeviceId.Size = new System.Drawing.Size(368, 28);
            this.txtDeviceId.TabIndex = 36;
            this.txtDeviceId.TextChanged += new System.EventHandler(this.txtDeviceId_TextChanged);
            // 
            // label3
            // 
            this.label3.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.label3.Location = new System.Drawing.Point(478, 92);
            this.label3.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(95, 18);
            this.label3.TabIndex = 35;
            this.label3.Text = "设备ID";
            this.label3.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // txtDeviceSecret
            // 
            this.txtDeviceSecret.Location = new System.Drawing.Point(1086, 83);
            this.txtDeviceSecret.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.txtDeviceSecret.Name = "REPLACE_WITH_YOUR_VALUE";
            this.txtDeviceSecret.PasswordChar = '*';
            this.txtDeviceSecret.Size = new System.Drawing.Size(188, 28);
            this.txtDeviceSecret.TabIndex = 38;
            // 
            // label7
            // 
            this.label7.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.label7.Location = new System.Drawing.Point(952, 90);
            this.label7.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(128, 18);
            this.label7.TabIndex = 37;
            this.label7.Text = "设备密钥";
            this.label7.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // linkLabel1
            // 
            this.linkLabel1.AutoSize = true;
            this.linkLabel1.Location = new System.Drawing.Point(1194, 198);
            this.linkLabel1.Name = "linkLabel1";
            this.linkLabel1.Size = new System.Drawing.Size(80, 18);
            this.linkLabel1.TabIndex = 39;
            this.linkLabel1.TabStop = true;
            this.linkLabel1.Text = "清空日志";
            this.linkLabel1.LinkClicked += new System.Windows.Forms.LinkLabelLinkClickedEventHandler(this.linkLabel1_LinkClicked);
            // 
            // cbReconnect
            // 
            this.cbReconnect.AutoSize = true;
            this.cbReconnect.Location = new System.Drawing.Point(262, 32);
            this.cbReconnect.Margin = new System.Windows.Forms.Padding(3, 4, 3, 4);
            this.cbReconnect.Name = "cbReconnect";
            this.cbReconnect.Size = new System.Drawing.Size(178, 22);
            this.cbReconnect.TabIndex = 40;
            this.cbReconnect.Text = "是否启用退避重连";
            this.cbReconnect.UseVisualStyleBackColor = true;
            this.cbReconnect.Click += new System.EventHandler(this.cbReconnect_Click);
            // 
            // comcaozuo
            // 
            this.comcaozuo.Controls.Add(this.XuanZeChuanKou);
            this.comcaozuo.Controls.Add(this.comboPortName);
            this.comcaozuo.Controls.Add(this.buttonOpenCloseCom);
            this.comcaozuo.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.comcaozuo.Location = new System.Drawing.Point(4, 794);
            this.comcaozuo.Margin = new System.Windows.Forms.Padding(4);
            this.comcaozuo.Name = "comcaozuo";
            this.comcaozuo.Padding = new System.Windows.Forms.Padding(4);
            this.comcaozuo.Size = new System.Drawing.Size(699, 141);
            this.comcaozuo.TabIndex = 51;
            this.comcaozuo.TabStop = false;
            this.comcaozuo.Text = "串口操作";
            // 
            // XuanZeChuanKou
            // 
            this.XuanZeChuanKou.AutoSize = true;
            this.XuanZeChuanKou.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.XuanZeChuanKou.Location = new System.Drawing.Point(9, 57);
            this.XuanZeChuanKou.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.XuanZeChuanKou.Name = "XuanZeChuanKou";
            this.XuanZeChuanKou.Size = new System.Drawing.Size(210, 41);
            this.XuanZeChuanKou.TabIndex = 40;
            this.XuanZeChuanKou.Text = "请选择串口：";
            // 
            // comboPortName
            // 
            this.comboPortName.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.comboPortName.FormattingEnabled = true;
            this.comboPortName.Location = new System.Drawing.Point(238, 51);
            this.comboPortName.Margin = new System.Windows.Forms.Padding(4);
            this.comboPortName.Name = "comboPortName";
            this.comboPortName.Size = new System.Drawing.Size(144, 49);
            this.comboPortName.TabIndex = 41;
            this.comboPortName.SelectedIndexChanged += new System.EventHandler(this.comboPortName_SelectedIndexChanged);
            // 
            // buttonOpenCloseCom
            // 
            this.buttonOpenCloseCom.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.buttonOpenCloseCom.Location = new System.Drawing.Point(534, 52);
            this.buttonOpenCloseCom.Margin = new System.Windows.Forms.Padding(4);
            this.buttonOpenCloseCom.Name = "buttonOpenCloseCom";
            this.buttonOpenCloseCom.Size = new System.Drawing.Size(156, 52);
            this.buttonOpenCloseCom.TabIndex = 44;
            this.buttonOpenCloseCom.Text = "打开串口";
            this.buttonOpenCloseCom.UseVisualStyleBackColor = true;
            this.buttonOpenCloseCom.Click += new System.EventHandler(this.buttonOpenCloseCom_Click);
            // 
            // WenShiDuShuju
            // 
            this.WenShiDuShuju.Controls.Add(this.label_shidu);
            this.WenShiDuShuju.Controls.Add(this.label_wenduzhi);
            this.WenShiDuShuju.Controls.Add(this.ShiDuZhi);
            this.WenShiDuShuju.Controls.Add(this.WenDuZhi);
            this.WenShiDuShuju.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.WenShiDuShuju.Location = new System.Drawing.Point(720, 779);
            this.WenShiDuShuju.Margin = new System.Windows.Forms.Padding(4);
            this.WenShiDuShuju.Name = "WenShiDuShuju";
            this.WenShiDuShuju.Padding = new System.Windows.Forms.Padding(4);
            this.WenShiDuShuju.Size = new System.Drawing.Size(563, 156);
            this.WenShiDuShuju.TabIndex = 53;
            this.WenShiDuShuju.TabStop = false;
            this.WenShiDuShuju.Text = "温湿度";
            // 
            // label_shidu
            // 
            this.label_shidu.AutoSize = true;
            this.label_shidu.Location = new System.Drawing.Point(350, 72);
            this.label_shidu.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label_shidu.Name = "label_shidu";
            this.label_shidu.Size = new System.Drawing.Size(90, 41);
            this.label_shidu.TabIndex = 3;
            this.label_shidu.Text = "湿度:";
            // 
            // label_wenduzhi
            // 
            this.label_wenduzhi.AutoSize = true;
            this.label_wenduzhi.Location = new System.Drawing.Point(33, 72);
            this.label_wenduzhi.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label_wenduzhi.Name = "label_wenduzhi";
            this.label_wenduzhi.Size = new System.Drawing.Size(114, 41);
            this.label_wenduzhi.TabIndex = 2;
            this.label_wenduzhi.Text = "温度：";
            // 
            // ShiDuZhi
            // 
            this.ShiDuZhi.Location = new System.Drawing.Point(468, 66);
            this.ShiDuZhi.Margin = new System.Windows.Forms.Padding(4);
            this.ShiDuZhi.Multiline = true;
            this.ShiDuZhi.Name = "ShiDuZhi";
            this.ShiDuZhi.Size = new System.Drawing.Size(92, 56);
            this.ShiDuZhi.TabIndex = 1;
            this.ShiDuZhi.TextChanged += new System.EventHandler(this.ShiDuZhi_TextChanged);
            // 
            // WenDuZhi
            // 
            this.WenDuZhi.Location = new System.Drawing.Point(154, 66);
            this.WenDuZhi.Margin = new System.Windows.Forms.Padding(4);
            this.WenDuZhi.Multiline = true;
            this.WenDuZhi.Name = "WenDuZhi";
            this.WenDuZhi.Size = new System.Drawing.Size(92, 56);
            this.WenDuZhi.TabIndex = 0;
            this.WenDuZhi.TextChanged += new System.EventHandler(this.WenDuZhi_TextChanged);
            // 
            // FrmMqttDemo
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 18F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1287, 948);
            this.Controls.Add(this.WenShiDuShuju);
            this.Controls.Add(this.comcaozuo);
            this.Controls.Add(this.cbReconnect);
            this.Controls.Add(this.linkLabel1);
            this.Controls.Add(this.txtDeviceSecret);
            this.Controls.Add(this.label7);
            this.Controls.Add(this.txtDeviceId);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.txtServerUri);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.btnConnect);
            this.Controls.Add(this.btnDisconnect);
            this.Controls.Add(this.cbOosSelect);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.cbSSLConnect);
            this.Controls.Add(this.btnSubscribe);
            this.Controls.Add(this.btnPublish);
            this.Controls.Add(this.txtSendMessage);
            this.Controls.Add(this.txtPubTopic);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.txtReceiveMessage);
            this.Controls.Add(this.txtSubTopic);
            this.Controls.Add(this.label1);
            this.Margin = new System.Windows.Forms.Padding(3, 4, 3, 4);
            this.Name = "FrmMqttDemo";
            this.Text = "MQTT设备接入模拟";
            this.Load += new System.EventHandler(this.FrmMqttDemo_Load);
            this.comcaozuo.ResumeLayout(false);
            this.comcaozuo.PerformLayout();
            this.WenShiDuShuju.ResumeLayout(false);
            this.WenShiDuShuju.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button btnSubscribe;
        private System.Windows.Forms.Button btnPublish;
        private System.Windows.Forms.TextBox txtSendMessage;
        private System.Windows.Forms.TextBox txtPubTopic;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox txtReceiveMessage;
        private System.Windows.Forms.TextBox txtSubTopic;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.CheckBox cbSSLConnect;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.ComboBox cbOosSelect;
        private System.Windows.Forms.Button btnDisconnect;
        private System.Windows.Forms.Button btnConnect;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.TextBox txtServerUri;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.TextBox txtDeviceId;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox txtDeviceSecret;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.LinkLabel linkLabel1;
        private System.Windows.Forms.CheckBox cbReconnect;
        private System.Windows.Forms.GroupBox comcaozuo;
        private System.Windows.Forms.Label XuanZeChuanKou;
        private System.Windows.Forms.ComboBox comboPortName;
        private System.Windows.Forms.Button buttonOpenCloseCom;
        private System.Windows.Forms.GroupBox WenShiDuShuju;
        private System.Windows.Forms.Label label_shidu;
        private System.Windows.Forms.Label label_wenduzhi;
        private System.Windows.Forms.TextBox ShiDuZhi;
        private System.Windows.Forms.TextBox WenDuZhi;
    }
}