from tkinter import *

cnt=0
total=0

def Ok():
    global cnt,total
    cnt+=1
    num.set(f"员工人数：{cnt}")
    lab_num.config(textvariable=num)
    s=float(ent.get())
    total+=s
    avg.set(f"平均工资：{total/cnt}")
    lab_avg.config(textvariable=avg)
    
root=Tk()
root.title('工资统计')
root.geometry('800x600')

img=PhotoImage(file='1.png')
lab0=Label(root,image=img)
lab0.place(relx=0.6,rely=0.1)

lab=Label(root,text='请输入员工工资：')
lab.place(relx=0.1,rely=0.2)

v=StringVar()
ent=Entry(root,textvariable=v)
ent.place(relx=0.1,rely=0.3)

num=StringVar()
num.set(f"员工人数：0")
lab_num=Label(root,textvariable=num)
lab_num.place(relx=0.1,rely=0.5)

avg=StringVar()
avg.set(f"平均工资：0")
lab_avg=Label(root,textvariable=avg)
lab_avg.place(relx=0.1,rely=0.6)

button_Quit=Button(root,text='Quit',command=root.quit)
button_Quit.place(relx=0.1,rely=0.1)

button_Ok=Button(root,text='Ok',command=Ok)
button_Ok.place(relx=0.1,rely=0.4)

text=StringVar()
Text=Label(root,textvariable=text)
Text.place(relx=0.25,rely=0.8)

root.mainloop()
