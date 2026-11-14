import time as t
from tkinter import *

def gettime():
    v_time.set(t.strftime('%Y-%m-%d %H:%M:%S'))
    root.after(1000,gettime)
    
def cancel():
    v.set('')
    
def ok():
    f=open(r'E:\college\Python\实验四\register.txt','a',encoding='utf-8')
    f.write(str('注册时间：'+v_time.get()+'\n'))
    f.write(str('用户名：'+v_id.get()+'\n'))
    f.write(str('真实姓名：'+v_name.get()+'\n'))
    f.write(str('手机号码：'+v_num.get()+'\n'))
    f.write(str('QQ：'+v_qq.get()+'\n'))
    f.write(str('E-mail：'+v_mail.get()+'\n'))
    f.close()

root=Tk()
root.geometry('500x350')
root['bg']='plum'
root.title('注册用户')

Label(root,text='[*真实姓名]为必填项。').place(x=200,y=5)
Label(root,text='*真实姓名').place(x=0,y=145)

Label(root,text='*用户名').place(x=0,y=110)

Label(root,text='[*手机号码]为必填项。').place(x=200,y=40)
Label(root,text='*手机号码').place(x=0,y=180)

Label(root,text='QQ').place(x=0,y=215)

Label(root,text='[*E-mail]为必填项。').place(x=200,y=75)
Label(root,text='*E-mail').place(x=0,y=250)

v_name=StringVar()
Entry(root,textvariable=v_name).place(x=70,y=145,width=430)

v_id=StringVar()
Entry(root,textvariable=v_id).place(x=70,y=110,width=430)

v_num=StringVar()
Entry(root,textvariable=v_num).place(x=70,y=180,width=430)

v_qq=StringVar()
Entry(root,textvariable=v_qq).place(x=70,y=215,width=430)

v_mail=StringVar()
Entry(root,textvariable=v_mail).place(x=70,y=250,width=430)

Button(root,text='Cancel',command=cancel).place(x=180,y=300)
Button(root,text='OK',command=ok).place(x=250,y=300)

v_time=StringVar()
Label(root,textvariable=v_time,font=('隶书',10)).place(x=0,y=5)
gettime()

root.mainloop()
