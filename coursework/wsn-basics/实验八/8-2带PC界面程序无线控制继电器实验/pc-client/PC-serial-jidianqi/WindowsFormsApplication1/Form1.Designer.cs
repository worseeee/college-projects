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
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(1, 56);
            this.label1.Margin = new System.Windows.Forms.Padding(7, 0, 7, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(210, 41);
            this.label1.TabIndex = 4;
            this.label1.Text = "请选择串口：";
            // 
            // comboPortName
            // 
            this.comboPortName.FormattingEnabled = true;
            this.comboPortName.Location = new System.Drawing.Point(183, 53);
            this.comboPortName.Margin = new System.Windows.Forms.Padding(7);
            this.comboPortName.Name = "comboPortName";
            this.comboPortName.Size = new System.Drawing.Size(149, 49);
            this.comboPortName.TabIndex = 5;
            this.comboPortName.SelectedIndexChanged += new System.EventHandler(this.comboPortName_SelectedIndexChanged);
            // 
            // buttonOpenClosecom
            // 
            this.buttonOpenClosecom.Location = new System.Drawing.Point(100, 116);
            this.buttonOpenClosecom.Margin = new System.Windows.Forms.Padding(7);
            this.buttonOpenClosecom.Name = "buttonOpenClosecom";
            this.buttonOpenClosecom.Size = new System.Drawing.Size(163, 54);
            this.buttonOpenClosecom.TabIndex = 34;
            this.buttonOpenClosecom.Text = "打开串口";
            this.buttonOpenClosecom.UseVisualStyleBackColor = true;
            this.buttonOpenClosecom.Click += new System.EventHandler(this.buttonOpenClosecom_Click);
            // 
            // buttonOpenLight
            // 
            this.buttonOpenLight.Location = new System.Drawing.Point(8, 184);
            this.buttonOpenLight.Margin = new System.Windows.Forms.Padding(7);
            this.buttonOpenLight.Name = "buttonOpenLight";
            this.buttonOpenLight.Size = new System.Drawing.Size(164, 54);
            this.buttonOpenLight.TabIndex = 37;
            this.buttonOpenLight.Text = "开继电器";
            this.buttonOpenLight.UseVisualStyleBackColor = true;
            this.buttonOpenLight.Click += new System.EventHandler(this.buttonOpenLight_Click);
            // 
            // buttonCloseLight
            // 
            this.buttonCloseLight.Location = new System.Drawing.Point(193, 184);
            this.buttonCloseLight.Margin = new System.Windows.Forms.Padding(7);
            this.buttonCloseLight.Name = "buttonCloseLight";
            this.buttonCloseLight.Size = new System.Drawing.Size(157, 54);
            this.buttonCloseLight.TabIndex = 38;
            this.buttonCloseLight.Text = "关继电器";
            this.buttonCloseLight.UseVisualStyleBackColor = true;
            this.buttonCloseLight.Click += new System.EventHandler(this.buttonCloseLight_Click);
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(8, 248);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(342, 49);
            this.textBox1.TabIndex = 41;
            this.textBox1.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            // 
            // PCZigbeeLed
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(19F, 41F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(366, 298);
            this.Controls.Add(this.textBox1);
            this.Controls.Add(this.buttonCloseLight);
            this.Controls.Add(this.buttonOpenLight);
            this.Controls.Add(this.buttonOpenClosecom);
            this.Controls.Add(this.comboPortName);
            this.Controls.Add(this.label1);
            this.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.Margin = new System.Windows.Forms.Padding(7);
            this.Name = "PCZigbeeLed";
            this.Text = "8-2";
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
        private System.Windows.Forms.TextBox textBox1;
    }
}

