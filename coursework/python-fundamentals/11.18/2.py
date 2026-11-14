from tkinter import *

def display():
    a=ent.get()
    text.set(f"{a}")
    Text.config(textvariable=text)
    
root=Tk()
root.title('文本显示')
root.geometry('800x600')

img=PhotoImage(file='1.png')
lab0=Label(root,image=img)
lab0.place(relx=0.6,rely=0.1)

ent=Entry(root)
ent.place(relx=0.2,rely=0.2)

button=Button(root,text='显示',command=display)
button.place(relx=0.25,rely=0.5)

text=StringVar()
Text=Label(root,textvariable=text)
Text.place(relx=0.25,rely=0.8)

root.mainloop()
