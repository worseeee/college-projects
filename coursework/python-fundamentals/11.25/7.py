from tkinter import *

def font():
    style=''
    if v1.get()==1:
        style+='bold '
    if v2.get()==1:
        style+='italic '
    lab.config(font=('Arial',10,style))

def color():
    if v.get()==1:
        lab.config(fg='red')
    if v.get()==2:
        lab.config(fg='yellow')
    if v.get()==3:
        lab.config(fg='blue')
    
root=Tk()
root.geometry('250x180')
root.title('练习7')
root['bg']='teal'

v=IntVar()
Radiobutton(root,variable=v,text='红',value=1,command=color).pack()
Radiobutton(root,variable=v,text='黄',value=2,command=color).pack()
Radiobutton(root,variable=v,text='蓝',value=3,command=color).pack()

v1=IntVar()
v2=IntVar()
Checkbutton(root,variable=v1,text='粗体',command=font).pack()
Checkbutton(root,variable=v2,text='斜体',command=font).pack()

lab=Label(root,text='hello,world!')
lab.pack()

root.mainloop()
