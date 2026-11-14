namespace tempsensor
{
    partial class Form1
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
            this.comboPortName = new System.Windows.Forms.ComboBox();
            this.XuanZeChuanKou = new System.Windows.Forms.Label();
            this.buttonOpenCloseCom = new System.Windows.Forms.Button();
            this.comcaozuo = new System.Windows.Forms.GroupBox();
            this.WenDuShuju = new System.Windows.Forms.GroupBox();
            this.WenDuZhi = new System.Windows.Forms.TextBox();
            this.灯控 = new System.Windows.Forms.GroupBox();
            this.buttonCloseLight = new System.Windows.Forms.Button();
            this.buttonOpenLight = new System.Windows.Forms.Button();
            this.textBoxThreshhold = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.buttonMode = new System.Windows.Forms.Button();
            this.comcaozuo.SuspendLayout();
            this.WenDuShuju.SuspendLayout();
            this.灯控.SuspendLayout();
            this.SuspendLayout();
            // 
            // comboPortName
            // 
            this.comboPortName.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.comboPortName.FormattingEnabled = true;
            this.comboPortName.Location = new System.Drawing.Point(238, 51);
            this.comboPortName.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
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
            this.buttonOpenCloseCom.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
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
            this.comcaozuo.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.comcaozuo.Name = "comcaozuo";
            this.comcaozuo.Padding = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.comcaozuo.Size = new System.Drawing.Size(699, 141);
            this.comcaozuo.TabIndex = 50;
            this.comcaozuo.TabStop = false;
            this.comcaozuo.Text = "串口操作";
            // 
            // WenDuShuju
            // 
            this.WenDuShuju.Controls.Add(this.label1);
            this.WenDuShuju.Controls.Add(this.textBoxThreshhold);
            this.WenDuShuju.Controls.Add(this.WenDuZhi);
            this.WenDuShuju.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.WenDuShuju.Location = new System.Drawing.Point(26, 225);
            this.WenDuShuju.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.WenDuShuju.Name = "WenDuShuju";
            this.WenDuShuju.Padding = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.WenDuShuju.Size = new System.Drawing.Size(699, 156);
            this.WenDuShuju.TabIndex = 52;
            this.WenDuShuju.TabStop = false;
            this.WenDuShuju.Text = "温度";
            // 
            // WenDuZhi
            // 
            this.WenDuZhi.Location = new System.Drawing.Point(79, 66);
            this.WenDuZhi.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.WenDuZhi.Multiline = true;
            this.WenDuZhi.Name = "WenDuZhi";
            this.WenDuZhi.Size = new System.Drawing.Size(92, 56);
            this.WenDuZhi.TabIndex = 0;
            this.WenDuZhi.TextChanged += new System.EventHandler(this.WenDuZhi_TextChanged_1);
            // 
            // 灯控
            // 
            this.灯控.Controls.Add(this.buttonCloseLight);
            this.灯控.Controls.Add(this.buttonOpenLight);
            this.灯控.Font = new System.Drawing.Font("微软雅黑", 14.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.灯控.Location = new System.Drawing.Point(20, 420);
            this.灯控.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.灯控.Name = "灯控";
            this.灯控.Padding = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.灯控.Size = new System.Drawing.Size(720, 138);
            this.灯控.TabIndex = 53;
            this.灯控.TabStop = false;
            this.灯控.Text = "灯控";
            // 
            // buttonCloseLight
            // 
            this.buttonCloseLight.Location = new System.Drawing.Point(489, 60);
            this.buttonCloseLight.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.buttonCloseLight.Name = "buttonCloseLight";
            this.buttonCloseLight.Size = new System.Drawing.Size(206, 48);
            this.buttonCloseLight.TabIndex = 1;
            this.buttonCloseLight.Text = "关灯";
            this.buttonCloseLight.UseVisualStyleBackColor = true;
            this.buttonCloseLight.Click += new System.EventHandler(this.buttonCloseLight_Click);
            // 
            // buttonOpenLight
            // 
            this.buttonOpenLight.Location = new System.Drawing.Point(38, 57);
            this.buttonOpenLight.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.buttonOpenLight.Name = "buttonOpenLight";
            this.buttonOpenLight.Size = new System.Drawing.Size(183, 52);
            this.buttonOpenLight.TabIndex = 0;
            this.buttonOpenLight.Text = "开灯";
            this.buttonOpenLight.UseVisualStyleBackColor = true;
            this.buttonOpenLight.Click += new System.EventHandler(this.buttonOpenLight_click);
            // 
            // textBoxThreshhold
            // 
            this.textBoxThreshhold.Location = new System.Drawing.Point(494, 66);
            this.textBoxThreshhold.Margin = new System.Windows.Forms.Padding(4);
            this.textBoxThreshhold.Multiline = true;
            this.textBoxThreshhold.Name = "textBoxThreshhold";
            this.textBoxThreshhold.Size = new System.Drawing.Size(92, 56);
            this.textBoxThreshhold.TabIndex = 1;
            this.textBoxThreshhold.Text = "15";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label1.Location = new System.Drawing.Point(254, 69);
            this.label1.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(178, 41);
            this.label1.TabIndex = 45;
            this.label1.Text = "温度阈值：";
            // 
            // buttonMode
            // 
            this.buttonMode.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.buttonMode.Location = new System.Drawing.Point(287, 609);
            this.buttonMode.Margin = new System.Windows.Forms.Padding(4);
            this.buttonMode.Name = "buttonMode";
            this.buttonMode.Size = new System.Drawing.Size(156, 52);
            this.buttonMode.TabIndex = 45;
            this.buttonMode.Text = "模式转换";
            this.buttonMode.UseVisualStyleBackColor = true;
            this.buttonMode.Click += new System.EventHandler(this.buttonMode_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 18F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(758, 702);
            this.Controls.Add(this.buttonMode);
            this.Controls.Add(this.灯控);
            this.Controls.Add(this.WenDuShuju);
            this.Controls.Add(this.comcaozuo);
            this.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.Name = "Form1";
            this.Text = "10-2";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.comcaozuo.ResumeLayout(false);
            this.comcaozuo.PerformLayout();
            this.WenDuShuju.ResumeLayout(false);
            this.WenDuShuju.PerformLayout();
            this.灯控.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.ComboBox comboPortName;
        private System.Windows.Forms.Label XuanZeChuanKou;
        private System.Windows.Forms.Button buttonOpenCloseCom;
        private System.Windows.Forms.GroupBox comcaozuo;
        private System.Windows.Forms.GroupBox WenDuShuju;
        private System.Windows.Forms.TextBox WenDuZhi;
        private System.Windows.Forms.GroupBox 灯控;
        private System.Windows.Forms.Button buttonOpenLight;
        private System.Windows.Forms.Button buttonCloseLight;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox textBoxThreshhold;
        private System.Windows.Forms.Button buttonMode;
    }
}

