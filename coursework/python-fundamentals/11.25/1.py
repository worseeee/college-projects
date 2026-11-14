from tkinter import *

def callchk():
    str="选择了"
    if v1.get()==1:
        str+="物联网!"
    if v2.get()==1:
        str+="网络安全！"
    if v3.get()==1:
        str+="通信工程！"
    lab.config(text=str)

root=Tk()
root.geometry('250x120')
root.title('练习1')
root['bg']='teal'

v1=IntVar()
v2=IntVar()
v3=IntVar()

Checkbutton(root,variable=v1,text='物联网',command=callchk).pack()
Checkbutton(root,variable=v2,text='网络安全',command=callchk).pack()
Checkbutton(root,variable=v3,text='通信工程',command=callchk).pack()

lab=Label(root,text='这是标签对象')
lab.pack()

root.mainloop()
