import time as t
from tkinter import *

def gettime():
    v_time.set(t.strftime('%Y-%m-%d %H:%M:%S'))
    root.after(1000,gettime)
    
def callchk():
    str="我喜欢"
    if v.get()==1:
        str+="猫"
    if v.get()==2:
        str+="狗"
    if v.get()==3:
        str+="兔"
    str+=v_time.get()
    lab.config(text=str)

root=Tk()
root.geometry('250x120')
root.title('练习2')
root['bg']='teal'

v=IntVar()
v_time=StringVar()

Radiobutton(root,variable=v,text='猫',value=1,command=callchk).pack()
Radiobutton(root,variable=v,text='狗',value=2,command=callchk).pack()
Radiobutton(root,variable=v,text='兔',value=3,command=callchk).pack()

lab=Label(root,text='演示标签')
lab.pack()

gettime()
root.mainloop()
