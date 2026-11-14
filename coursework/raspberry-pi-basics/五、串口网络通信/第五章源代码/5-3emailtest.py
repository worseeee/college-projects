import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

email_host = 'smtp.qq.com'
email_port = 465
email_passwd = 'REPLACE_WITH_YOUR_VALUE'  # 这个是发送QQ账号的授权码，而不是QQ账号的密码，否则发送会失败

sender = 'student@example.com'  # 发送账号
receivers = ['student@example.com', 'student@example.com']  # 接收账号

msg = MIMEMultipart()
msg['Subject'] = 'Email from Raspberry Pi 4B'
msg['From'] = sender
msg['To'] = ';'.join(receivers)

msg_text = MIMEText(_text='hello, this email come from student@example.com', _subtype='plain', _charset='utf-8')
msg.attach(msg_text)

att = MIMEText(_text=open('./att.txt', 'rb').read(), _subtype='base64', _charset='utf-8')
att['Content-Type'] = 'application/octet-stream'
att['Content-Disposition'] = 'attachment; filename="att.txt"'
msg.attach(att)

try:
    smtpObj = smtplib.SMTP_SSL(host=email_host, port=email_port)
    smtpObj.login(sender, email_passwd)
    smtpObj.sendmail(sender, receivers, msg.as_string())
    print("Successfully sent email")
    smtpObj.close()
except smtplib.SMTPException as e:
    print("Error: unable to send email")
    print(e)