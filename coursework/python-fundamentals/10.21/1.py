a=eval(input("请输入第一个数："))
b=eval(input("请输入第二个数："))
if a<b:
    a,b=b,a
def GBS(a,b):
    m=a
    n=b
    while a%b!=0:
        a=a%b
        a,b=b,a
    x=m/b
    y=n/b
    c=b*x*y
    print("最大公约数为：",b)
    print("最小公倍数为：",c)
print(GBS(a,b))
