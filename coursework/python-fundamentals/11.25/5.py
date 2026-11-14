from tkinter import *
from random import *

num=randint(100,800)
low=100
high=800
cnt=0

def Start():
    global low,high,cnt
    cnt+=1
    a.set(f"{cnt}")
    lab_a.config(textvariable=a)
    if v.get()==num:
        t='恭喜你猜对啦！'
        lab.config(text=t)
    elif v.get()<num:
        low=v.get()
        m.set(f"{v.get()}")
        lab_m.config(textvariable=m)
        t='往大点猜试试看！'
        lab.config(text=t)
    else:
        high=v.get()
        n.set(f"{v.get()}")
        lab_n.config(textvariable=n)
        t='往小点猜试试看！'
        lab.config(text=t)
    
root=Tk()
root.title('练习5')
root.geometry('400x300')

img=PhotoImage(file='1.png')
lab0=Label(root,image=img)
lab0.place(relx=0.6,rely=0.1)

Label(root,text='数字炸弹').place(x=0,y=10)
Label(root,text='请输入：').place(x=0,y=70)

m=StringVar()
m.set(f"100")
lab_m=Label(root,textvariable=m)
lab_m.place(x=0,y=130)

n=StringVar()
n.set(f"800")
lab_n=Label(root,textvariable=n)
lab_n.place(x=50,y=130)

a=StringVar()
a.set(f"0")
lab_a=Label(root,textvariable=a)
lab_a.place(x=100,y=130)

v=IntVar()
ent=Entry(root,textvariable=v)
ent.place(x=50,y=70)

lab=Label(root,text='猜猜我是谁')
lab.place(x=0,y=190)

Button(root,text='开始',command=Start).place(x=0,y=250)

Button(root,text='退出',command=root.quit).place(x=50,y=250)

root.mainloop()
