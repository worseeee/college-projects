using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace device_demo_mqttnet.Utility
{
    class MultiLanguage
    {
        /// <summary>
        /// 修改默认语言
        /// </summary>
        /// <param name="lang">待设置默认语言</param>
        public static void SetDefaultLanguage(string lang)
        {
            System.Threading.Thread.CurrentThread.CurrentUICulture = new System.Globalization.CultureInfo(lang);
        }

        /// <summary>
        /// 加载语言
        /// </summary>
        /// <param name="form">加载语言的窗口</param>
        /// <param name="formType">窗口的类型</param>
        public static void LoadLanguage(Form form, Type formType)
        {
            if (form != null)
            {
                System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(formType);
                resources.ApplyResources(form, "$this");
                Loading(form, resources);
            }
        }

        /// <summary>
        /// 加载语言
        /// </summary>
        /// <param name="control">控件</param>
        /// <param name="resources">语言资源</param>
        private static void Loading(Control control, System.ComponentModel.ComponentResourceManager resources)
        {
            foreach (Control c in control.Controls)
            {
                resources.ApplyResources(c, c.Name);
                Loading(c, resources);
            }
        }
    }
}
