import turtle
import time
import math

start_time = time.time()

screen = turtle.Screen()
screen.title("小球滚动动画")
screen.bgcolor("lightblue")
screen.setup(800, 600)

big_ball = turtle.Turtle()
big_ball.speed(0)
big_ball.color("white")
big_ball.pensize(3)
big_ball.penup()
big_ball.goto(0, -100)
big_ball.pendown()
big_ball.circle(100)

small_ball = turtle.Turtle()
small_ball.speed(0)
small_ball.color("red")
small_ball.shape("circle")
small_ball.shapesize(2)  # 小球大小
small_ball.penup()

text_turtle = turtle.Turtle()
text_turtle.speed(0)
text_turtle.color("black")
text_turtle.penup()
text_turtle.hideturtle()

text_turtle.goto(0, 250)
text_turtle.write("姓名：刘胜炜    学号：0000000000", align="center", font=("楷体", 18, "bold"))

big_radius = 100
orbit_radius = 60  # 小球运动轨迹半径
center_x, center_y = 0, 0
angle = 0
angular_speed = 0.08

print("开始绘制动画...")

# 动画循环
for i in range(150):
    # 计算小球位置（在大球内部沿圆形轨迹运动）
    x = center_x + orbit_radius * math.cos(angle)
    y = center_y + orbit_radius * math.sin(angle)
    
    # 移动小球
    small_ball.goto(x, y)
    
    # 更新角度
    angle += angular_speed
    
    # 短暂延时
    time.sleep(0.03)

# 记录结束时间并计算总时间
end_time = time.time()
drawing_time = end_time - start_time

# 在图形下方显示画图时间和图形名称
text_turtle.goto(0, -280)
text_turtle.write(f"画图用时：{drawing_time:.2f}秒", 
                 align="center", font=("宋体", 16, "normal"))
text_turtle.goto(0, -310)
text_turtle.write("图形名称：大球内小球滚动动画", 
                 align="center", font=("宋体", 16, "normal"))

print(f"画图完成！总用时：{drawing_time:.2f}秒")

# 隐藏海龟光标
big_ball.hideturtle()

# 保持窗口打开
screen.mainloop()
