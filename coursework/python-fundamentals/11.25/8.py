from tkinter import *
def callb():
      root.config(bg=tf[int(v.get())])
root=Tk()
root.title('改变窗口背景颜色')
root.geometry('250x100')
v=StringVar()
v.set('2')
f=Frame(root,bd=4,relief=GROOVE)       
f.pack()
tf=['red','yellow','blue']
for n in range(len(tf)):
       r=Radiobutton(f,variable=v,text=tf[n],value=n,command=callb)
       r.grid(row=n,column=1,sticky=W)      
root.mainloop()
