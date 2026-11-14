from tkinter import *

def callchk():
    str="我喜欢"
    if (v1.get()==1 and v2.get()==1 and v3.get()==1 and v4.get()==1):
        str+="所有球类运动"
    else:
        if v1.get()==1:
            str+="足球  "
        if v2.get()==1:
            str+="篮球  "
        if v3.get()==1:
            str+="羽毛球  "
        if v4.get()==1:
            str+="乒乓球  "
    lab.config(text=str)

root=Tk()
root.geometry('250x180')
root.title('练习3')
root['bg']='teal'

v1=IntVar()
v2=IntVar()
v3=IntVar()
v4=IntVar()

Label(root,text='请选择您爱好的球类运动：').pack()

Checkbutton(root,variable=v1,text='足球',command=callchk).pack()
Checkbutton(root,variable=v2,text='篮球',command=callchk).pack()
Checkbutton(root,variable=v3,text='羽毛球',command=callchk).pack()
Checkbutton(root,variable=v4,text='乒乓球',command=callchk).pack()

Label(root,text='您爱好的球类运动是：').pack()

lab=Label(root,text='这是标签对象')
lab.pack()

root.mainloop()
