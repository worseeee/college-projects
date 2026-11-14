import random
target=random.randint(1,1000)
cnt=0
while True:
    a=eval(input("请输入："))
    cnt+=1
    if a>target:
        print("猜大了")
    elif a<target:
        print("猜小了")
    else:
        print("恭喜你经过",cnt,"次猜对了！")
        break
