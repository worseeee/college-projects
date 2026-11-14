namespace WindowsFormsApplication1
{
    partial class PCZigbeeLed
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
            this.label1 = new System.Windows.Forms.Label();
            this.comboPortName = new System.Windows.Forms.ComboBox();
            this.buttonOpenClosecom = new System.Windows.Forms.Button();
            this.buttonOpenLight = new System.Windows.Forms.Button();
            this.buttonCloseLight = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(26, 73);
            this.label1.Margin = new System.Windows.Forms.Padding(6, 0, 6, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(191, 38);
            this.label1.TabIndex = 4;
            this.label1.Text = "请选择串口：";
            // 
            // comboPortName
            // 
            this.comboPortName.FormattingEnabled = true;
            this.comboPortName.Location = new System.Drawing.Point(156, 66);
            this.comboPortName.Margin = new System.Windows.Forms.Padding(6);
            this.comboPortName.Name = "comboPortName";
            this.comboPortName.Size = new System.Drawing.Size(127, 46);
            this.comboPortName.TabIndex = 5;
            this.comboPortName.SelectedIndexChanged += new System.EventHandler(this.comboPortName_SelectedIndexChanged);
            // 
            // buttonOpenClosecom
            // 
            this.buttonOpenClosecom.Location = new System.Drawing.Point(313, 62);
            this.buttonOpenClosecom.Margin = new System.Windows.Forms.Padding(6);
            this.buttonOpenClosecom.Name = "buttonOpenClosecom";
            this.buttonOpenClosecom.Size = new System.Drawing.Size(108, 46);
            this.buttonOpenClosecom.TabIndex = 34;
            this.buttonOpenClosecom.Text = "打开串口";
            this.buttonOpenClosecom.UseVisualStyleBackColor = true;
            this.buttonOpenClosecom.Click += new System.EventHandler(this.buttonOpenClosecom_Click);
            // 
            // buttonOpenLight
            // 
            this.buttonOpenLight.Location = new System.Drawing.Point(31, 153);
            this.buttonOpenLight.Margin = new System.Windows.Forms.Padding(6);
            this.buttonOpenLight.Name = "buttonOpenLight";
            this.buttonOpenLight.Size = new System.Drawing.Size(107, 48);
            this.buttonOpenLight.TabIndex = 37;
            this.buttonOpenLight.Text = "开灯";
            this.buttonOpenLight.UseVisualStyleBackColor = true;
            this.buttonOpenLight.Click += new System.EventHandler(this.buttonOpenLight_Click);
            // 
            // buttonCloseLight
            // 
            this.buttonCloseLight.Location = new System.Drawing.Point(313, 153);
            this.buttonCloseLight.Margin = new System.Windows.Forms.Padding(6);
            this.buttonCloseLight.Name = "buttonCloseLight";
            this.buttonCloseLight.Size = new System.Drawing.Size(108, 48);
            this.buttonCloseLight.TabIndex = 38;
            this.buttonCloseLight.Text = "关灯";
            this.buttonCloseLight.UseVisualStyleBackColor = true;
            this.buttonCloseLight.Click += new System.EventHandler(this.buttonCloseLight_Click);
            // 
            // PCZigbeeLed
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(18F, 38F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(443, 247);
            this.Controls.Add(this.buttonCloseLight);
            this.Controls.Add(this.buttonOpenLight);
            this.Controls.Add(this.buttonOpenClosecom);
            this.Controls.Add(this.comboPortName);
            this.Controls.Add(this.label1);
            this.Font = new System.Drawing.Font("微软雅黑", 14.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.Margin = new System.Windows.Forms.Padding(6);
            this.Name = "PCZigbeeLed";
            this.Text = "6-3";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ComboBox comboPortName;
        private System.Windows.Forms.Button buttonOpenClosecom;
        private System.Windows.Forms.Button buttonOpenLight;
        private System.Windows.Forms.Button buttonCloseLight;
    }
}

