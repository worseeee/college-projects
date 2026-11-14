from turtle import *
setup(1000,1000)
i=0
color('yellow','yellow')
begin_fill()
while i<4:
    forward(200)
    left(90)
    i+=1
end_fill()
penup()
goto(30,-50)
pendown()
write('黄色四边形',font=('Arial',20,'normal'))
