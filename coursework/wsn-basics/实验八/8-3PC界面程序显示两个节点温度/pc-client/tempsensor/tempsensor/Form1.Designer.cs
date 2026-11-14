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
            this.WenDuZhi_3 = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.WenDuZhi_2 = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.WenDuZhi_1 = new System.Windows.Forms.TextBox();
            this.comcaozuo.SuspendLayout();
            this.WenDuShuju.SuspendLayout();
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
            // WenDuShuju
            // 
            this.WenDuShuju.Controls.Add(this.WenDuZhi_3);
            this.WenDuShuju.Controls.Add(this.label3);
            this.WenDuShuju.Controls.Add(this.WenDuZhi_2);
            this.WenDuShuju.Controls.Add(this.label2);
            this.WenDuShuju.Controls.Add(this.label1);
            this.WenDuShuju.Controls.Add(this.WenDuZhi_1);
            this.WenDuShuju.Font = new System.Drawing.Font("微软雅黑", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.WenDuShuju.Location = new System.Drawing.Point(26, 225);
            this.WenDuShuju.Margin = new System.Windows.Forms.Padding(4);
            this.WenDuShuju.Name = "WenDuShuju";
            this.WenDuShuju.Padding = new System.Windows.Forms.Padding(4);
            this.WenDuShuju.Size = new System.Drawing.Size(699, 156);
            this.WenDuShuju.TabIndex = 52;
            this.WenDuShuju.TabStop = false;
            this.WenDuShuju.Text = "温度";
            // 
            // WenDuZhi_3
            // 
            this.WenDuZhi_3.Location = new System.Drawing.Point(587, 73);
            this.WenDuZhi_3.Margin = new System.Windows.Forms.Padding(4);
            this.WenDuZhi_3.Name = "WenDuZhi_3";
            this.WenDuZhi_3.Size = new System.Drawing.Size(103, 49);
            this.WenDuZhi_3.TabIndex = 5;
            this.WenDuZhi_3.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(482, 76);
            this.label3.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(109, 41);
            this.label3.TabIndex = 4;
            this.label3.Text = "节点3:";
            this.label3.Click += new System.EventHandler(this.label3_Click);
            // 
            // WenDuZhi_2
            // 
            this.WenDuZhi_2.Location = new System.Drawing.Point(362, 73);
            this.WenDuZhi_2.Margin = new System.Windows.Forms.Padding(4);
            this.WenDuZhi_2.Name = "WenDuZhi_2";
            this.WenDuZhi_2.Size = new System.Drawing.Size(103, 49);
            this.WenDuZhi_2.TabIndex = 3;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(254, 76);
            this.label2.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(109, 41);
            this.label2.TabIndex = 2;
            this.label2.Text = "节点2:";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(28, 76);
            this.label1.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(109, 41);
            this.label1.TabIndex = 1;
            this.label1.Text = "节点1:";
            // 
            // WenDuZhi_1
            // 
            this.WenDuZhi_1.Location = new System.Drawing.Point(144, 72);
            this.WenDuZhi_1.Margin = new System.Windows.Forms.Padding(4);
            this.WenDuZhi_1.Multiline = true;
            this.WenDuZhi_1.Name = "WenDuZhi_1";
            this.WenDuZhi_1.Size = new System.Drawing.Size(92, 56);
            this.WenDuZhi_1.TabIndex = 0;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 18F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(759, 440);
            this.Controls.Add(this.WenDuShuju);
            this.Controls.Add(this.comcaozuo);
            this.Margin = new System.Windows.Forms.Padding(4);
            this.Name = "Form1";
            this.Text = "8-3";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.comcaozuo.ResumeLayout(false);
            this.comcaozuo.PerformLayout();
            this.WenDuShuju.ResumeLayout(false);
            this.WenDuShuju.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.ComboBox comboPortName;
        private System.Windows.Forms.Label XuanZeChuanKou;
        private System.Windows.Forms.Button buttonOpenCloseCom;
        private System.Windows.Forms.GroupBox comcaozuo;
        private System.Windows.Forms.GroupBox WenDuShuju;
        private System.Windows.Forms.TextBox WenDuZhi_1;
        private System.Windows.Forms.TextBox WenDuZhi_2;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox WenDuZhi_3;
        private System.Windows.Forms.Label label3;
    }
}

