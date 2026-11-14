import turtle
import time
import math
turtle.setup(1000,1000)
turtle.speed(0)
center_x,center_y=0,-50
angle=-90
i=0
while i<1000:
    turtle.hideturtle()
    turtle.penup()
    turtle.goto(-200,250)
    turtle.pendown()
    turtle.write('姓名：刘胜炜    学号：0000000000',font=('Arial',20,'normal'))
    start=time.perf_counter()
    turtle.penup()
    turtle.goto(0,-200)
    turtle.pendown()
    turtle.circle(200)
    turtle.penup()
    x=center_x+150*math.cos(math.radians(angle))
    y=center_y+150*math.sin(math.radians(angle))
    turtle.goto(x,y)
    turtle.pendown()
    turtle.color('black','orange')
    turtle.begin_fill()
    turtle.circle(50)
    turtle.end_fill()
    end=time.perf_counter()
    t=end-start
    turtle.penup()
    turtle.goto(-350,-250)
    turtle.pendown()
    turtle.write(f'画图时间：{t}秒    图形名称：小球滚动动画',font=('Arial',20,'normal'))
    turtle.penup()
    turtle.goto(0,-200)
    turtle.pendown()
    turtle.clear()
    angle+=90
    i+=1
    time.sleep(0.01)
