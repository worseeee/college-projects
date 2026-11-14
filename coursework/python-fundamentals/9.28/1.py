a=eval(input("请输入三角形的三条边长："))
b=eval(input("请输入三角形的三条边长："))
c=eval(input("请输入三角形的三条边长："))
arr=[a,b,c]
arr.sort()
if arr[0]+arr[1]>arr[2]:
    if a==b==c:
        print("构成等边三角形")
    elif a==b or a==c or b==c:
        print("构成等腰三角形")
    elif arr[0]**2+arr[1]**2==arr[2]**2:
        print("构成直角三角形")
    else:
        print("构成一般三角形")
else:
    print("不能构成三角形")


