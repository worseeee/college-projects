from turtle import *
setup(1000,1000)
i=0
color('red','red')
begin_fill()
while i<3:
    forward(200)
    left(120)
    i+=1
end_fill()
penup()
goto(25,-50)
pendown()
write('红色三角形',font=('Arial',20,'normal'))
