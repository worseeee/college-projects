from turtle import *
setup(1000,1000)
i=0
color('blue','blue')
begin_fill()
while i<6:
    forward(200)
    left(60)
    i+=1
end_fill()
penup()
goto(30,-50)
pendown()
write('蓝色六边形',font=('Arial',20,'normal'))
