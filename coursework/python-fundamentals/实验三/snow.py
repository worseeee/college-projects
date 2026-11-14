from turtle import *
from random import *
setup(1000,1000)
speed(3)
for i in range(10):
    x=randint(-400,400)
    y=randint(-400,400)
    dens=randint(4,10)
    snowsize=randint(10,100)
    r,g,b=random(),random(),random()
    pencolor(r,g,b)
    for j in range(dens):
        forward(snowsize)
        backward(snowsize)
        left(360/dens)
    penup()
    goto(x,y)
    pendown()

