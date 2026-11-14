disc={'cg':'123456','lzc':'abcde','zy':'basell','zcw':'123abc'}
print("字典：",disc)
disc['lsw']='wozuishuai666'
print("增加一个用户名和密码后的字典",disc)
del disc['zy']
print("删除一个用户名和密码后的字典",disc)
a=input("请输入用户名：")
if a in disc:
    b0=disc.get(a)
    b1=input("请输入密码：")
    if b1==b0:
        print("密码正确！")
    else:
        b2=input("密码错误1次！请重新输入：")
        if b2==b0:
            print("密码正确！")
        else:
            b3=input("密码错误2次！请重新输入：")
            if b3==b0:
                print("密码正确！")
            else:
                b4=input("密码错误3次！请重新输入：")
                if b4==b0:
                    print("密码正确！")
                else:
                    b5=input("密码错误4次！请重新输入：")
                    if b5==b0:
                        print("密码正确！")
                    else:
                        b6=print("密码错误5次！")
else:
    print("用户名不正确！")

    
