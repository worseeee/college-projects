import time as t
from tkinter import *

def gettime():
    v.set(t.strftime('%Y-%m-%d %H:%M:%S'))
    root.after(1000,gettime)

def add():
    lab_result.config(text='10')

def sub():
    lab_result.config(text='6')

def mul():
    lab_result.config(text='16')

def div():
    lab_result.config(text='4')

root=Tk()
root.title('加减乘除')
root.geometry('800x600')

img=PhotoImage(file='1.png')
lab0=Label(root,image=img)
lab0.place(relx=0.6,rely=0.1)

lab1=Label(root,text='8')
lab1.place(relx=0.1,rely=0.5)

lab2=Label(root,text='2')
lab2.place(relx=0.5,rely=0.5)

lab3=Label(root,text='=')
lab3.place(relx=0.7,rely=0.5)

lab_result=Label(root,text=' ')
lab_result.place(relx=0.9,rely=0.5)

button_add=Button(root,text='+',command=add)
button_add.place(relx=0.3,rely=0.2)
button_sub=Button(root,text='-',command=sub)
button_sub.place(relx=0.3,rely=0.4)
button_mul=Button(root,text='x',command=mul)
button_mul.place(relx=0.3,rely=0.6)
button_div=Button(root,text='/',command=div)
button_div.place(relx=0.3,rely=0.8)

v=StringVar()
lab_time=Label(root,textvariable=v,font=('隶书',10))
lab_time.pack()
gettime()

root.mainloop()
