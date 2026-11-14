from tkinter import *

def ok():
    f=open(r'E:\college\Python\11.25\6.txt','a',encoding='utf-8')
    f.write(str('姓名：'+v_name.get()+'\n'))
    f.write(str('学号：'+v_num.get()+'\n'))
    f.close()

def OK():
    t='我的兴趣爱好是：'
    if v1.get()==1:
        t+='唱歌  '
    if v2.get()==1:
        t+='阅读  '
    if v3.get()==1:
        t+='运动  '
    f=open(r'E:\college\Python\11.25\6.txt','a',encoding='utf-8')
    f.write(t+'\n')
    f.close()

def clear_widgets():
    for widget in root.winfo_children():
        if not isinstance(widget, (Radiobutton,)):
            widget.destroy()
            
def ivg():
    clear_widgets()
    if v.get()==0:
        Label(root,text='姓名：').place(x=50,y=80)
        ent_name=Entry(root,textvariable=v_name)
        ent_name.place(x=100,y=80)
        Label(root,text='学号：').place(x=50,y=120)
        ent_num=Entry(root,textvariable=v_num)
        ent_num.place(x=100,y=120)
        Button(root,text='OK',command=ok).place(x=150,y=160)
    if v.get()==1:
        Checkbutton(root,variable=v1,text='唱歌').place(x=120,y=60)
        Checkbutton(root,variable=v2,text='阅读').place(x=120,y=100)
        Checkbutton(root,variable=v3,text='运动').place(x=120,y=140)
        Button(root,text='确定',command=OK).place(x=130,y=170)
        
root=Tk()
root.geometry('300x200')
root.title('练习6')
root['bg']='teal'

v=IntVar()
Radiobutton(root,variable=v,text='个人信息',value=0,command=ivg).pack()
Radiobutton(root,variable=v,text='兴趣爱好',value=1,command=ivg).pack()

v_name=StringVar()
v_num=StringVar()

v1=IntVar()
v2=IntVar()
v3=IntVar()

root.mainloop()
