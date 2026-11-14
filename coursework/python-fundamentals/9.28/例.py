while True:
    a=input("请输入分数：（按q退出）")
    if a=='q':
        print('退出')
        break
    a=int(a)
    if a>=90:
        print('优秀')
    elif a>=80:
        print('良好')
    elif a>=70:
        print('中等')
    elif a>=60:
        print('及格')
    else:
        print('不及格')
