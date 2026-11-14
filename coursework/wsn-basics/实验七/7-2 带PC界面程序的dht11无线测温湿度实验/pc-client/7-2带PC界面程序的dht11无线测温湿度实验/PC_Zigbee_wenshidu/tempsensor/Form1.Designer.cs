namespace tempsensor
{
    partial class PC_Zigbee_wenshidu
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(PC_Zigbee_wenshidu));
            this.comboPortName = new System.Windows.Forms.ComboBox();
            this.XuanZeChuanKou = new System.Windows.Forms.Label();
            this.buttonOpenCloseCom = new System.Windows.Forms.Button();
            this.comcaozuo = new System.Windows.Forms.GroupBox();
            this.WenShiDuShuju = new System.Windows.Forms.GroupBox();
            this.label_shidu = new System.Windows.Forms.Label();
            this.label_wenduzhi = new System.Windows.Forms.Label();
            this.ShiDuZhi = new System.Windows.Forms.TextBox();
            this.WenDuZhi = new System.Windows.Forms.TextBox();
            this.DaoZeiBaoJing = new System.Windows.Forms.Button();
            this.axWindowsMediaPlayer1 = new AxWMPLib.AxWindowsMediaPlayer();
            this.comcaozuo.SuspendLayout();
            this.WenShiDuShuju.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.axWindowsMediaPlayer1)).BeginInit();
            this.SuspendLayout();
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
            // comcaozuo
            // 
            this.comcaozuo.Controls.Add(this.XuanZeChuanKou);
            this.comcaozuo.Controls.Add(this.comboPortName);
            this.comcaozuo.Controls.Add(this.buttonOpenCloseCom);
            this.comcaozuo.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.comcaozuo.Location = new System.Drawing.Point(26, 75);
            this.comcaozuo.Margin = new System.Windows.Forms.Padding(4);
            this.comcaozuo.Name = "comcaozuo";
            this.comcaozuo.Padding = new System.Windows.Forms.Padding(4);
            this.comcaozuo.Size = new System.Drawing.Size(699, 141);
            this.comcaozuo.TabIndex = 50;
            this.comcaozuo.TabStop = false;
            this.comcaozuo.Text = "串口操作";
            // 
            // WenShiDuShuju
            // 
            this.WenShiDuShuju.Controls.Add(this.label_shidu);
            this.WenShiDuShuju.Controls.Add(this.label_wenduzhi);
            this.WenShiDuShuju.Controls.Add(this.ShiDuZhi);
            this.WenShiDuShuju.Controls.Add(this.WenDuZhi);
            this.WenShiDuShuju.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.WenShiDuShuju.Location = new System.Drawing.Point(26, 225);
            this.WenShiDuShuju.Margin = new System.Windows.Forms.Padding(4);
            this.WenShiDuShuju.Name = "WenShiDuShuju";
            this.WenShiDuShuju.Padding = new System.Windows.Forms.Padding(4);
            this.WenShiDuShuju.Size = new System.Drawing.Size(699, 156);
            this.WenShiDuShuju.TabIndex = 52;
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
            // DaoZeiBaoJing
            // 
            this.DaoZeiBaoJing.BackColor = System.Drawing.Color.GreenYellow;
            this.DaoZeiBaoJing.Font = new System.Drawing.Font("微软雅黑", 18F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.DaoZeiBaoJing.Location = new System.Drawing.Point(221, 389);
            this.DaoZeiBaoJing.Margin = new System.Windows.Forms.Padding(4);
            this.DaoZeiBaoJing.Name = "DaoZeiBaoJing";
            this.DaoZeiBaoJing.Size = new System.Drawing.Size(255, 56);
            this.DaoZeiBaoJing.TabIndex = 53;
            this.DaoZeiBaoJing.Text = "温度报警";
            this.DaoZeiBaoJing.UseVisualStyleBackColor = false;
            // 
            // axWindowsMediaPlayer1
            // 
            this.axWindowsMediaPlayer1.Enabled = true;
            this.axWindowsMediaPlayer1.Location = new System.Drawing.Point(560, 405);
            this.axWindowsMediaPlayer1.Name = "axWindowsMediaPlayer1";
            this.axWindowsMediaPlayer1.OcxState = ((System.Windows.Forms.AxHost.State)(resources.GetObject("axWindowsMediaPlayer1.OcxState")));
            this.axWindowsMediaPlayer1.Size = new System.Drawing.Size(75, 23);
            this.axWindowsMediaPlayer1.TabIndex = 54;
            // 
            // PC_Zigbee_wenshidu
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 18F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(759, 440);
            this.Controls.Add(this.axWindowsMediaPlayer1);
            this.Controls.Add(this.DaoZeiBaoJing);
            this.Controls.Add(this.WenShiDuShuju);
            this.Controls.Add(this.comcaozuo);
            this.Margin = new System.Windows.Forms.Padding(4);
            this.Name = "PC_Zigbee_wenshidu";
            this.Text = "7-2";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.comcaozuo.ResumeLayout(false);
            this.comcaozuo.PerformLayout();
            this.WenShiDuShuju.ResumeLayout(false);
            this.WenShiDuShuju.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.axWindowsMediaPlayer1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.ComboBox comboPortName;
        private System.Windows.Forms.Label XuanZeChuanKou;
        private System.Windows.Forms.Button buttonOpenCloseCom;
        private System.Windows.Forms.GroupBox comcaozuo;
        private System.Windows.Forms.GroupBox WenShiDuShuju;
        private System.Windows.Forms.TextBox WenDuZhi;
        private System.Windows.Forms.Label label_shidu;
        private System.Windows.Forms.Label label_wenduzhi;
        private System.Windows.Forms.TextBox ShiDuZhi;
        private System.Windows.Forms.Button DaoZeiBaoJing;
        private AxWMPLib.AxWindowsMediaPlayer axWindowsMediaPlayer1;
    }
}

