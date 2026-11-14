import RPi.GPIO as GPIO
from time import sleep

rledpin = 32                          # 指定引脚，物理引脚编号32
gledpin = 33                          # 指定引脚，物理引脚编号33

GPIO.setwarnings(False)           

GPIO.setmode(GPIO.BOARD)              # 设置引脚编号系统，BOARD指的是物理引脚命名方式

GPIO.setup(rledpin,GPIO.OUT)          # 设置引脚32为输出
GPIO.setup(gledpin,GPIO.OUT)          # 设置引脚33为输出

pwm0 = GPIO.PWM(rledpin,50)           # 创建PWM0实例，并设置频率为50Hz
pwm1 = GPIO.PWM(gledpin,50)           # 创建PWM1实例，并设置频率为50Hz

while True:
    pwm0.start(0)                     # 启动PWM0实例，占空比为0
    for duty0 in range(0,101,5):      # 范围在0 - 100的占空比变化
        pwm0.ChangeDutyCycle(duty0)                   
        sleep(0.05)
      
    sleep(0.5)
    
    for duty0 in range(100,-1,-5):
        pwm0.ChangeDutyCycle(duty0)     
        sleep(0.05)
    
    sleep(0.5)
    pwm0.stop()                       # 停止PWM0实例
    
    pwm1.start(0)                     # 启动PWM1实例，占空比为0
    for duty1 in range(0,101,5):      # 范围在0 - 100的占空比变化
        pwm1.ChangeDutyCycle(duty1)                   
        sleep(0.05)
        
    sleep(0.5)
    
    for duty1 in range(100,-1,-5):
        pwm1.ChangeDutyCycle(duty1)     
        sleep(0.05)
    
    sleep(0.5)
    pwm1.stop()                       # 停止PWM1实例