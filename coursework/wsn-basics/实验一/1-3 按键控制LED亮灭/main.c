#include <ioCC2530.h>

typedef unsigned char uchar;
typedef unsigned int  uint;

#define LED1 P1_0       // P1.0口控制LED1
#define LED3 P1_4
#define KEY1 P0_1       // P0.1口控制S1

void DelayMS(uint msec)
{ 
    uint i,j;
    
    for (i=0; i<msec; i++)
        for (j=0; j<535; j++);
}

void LedOnOrOff(uchar mode)
{
    LED1 = mode;
    LED3 = mode; 
}

void InitLed(void)
{
    P1DIR |= 0x11;      //P1.0、P1.4定义为输出
    LedOnOrOff(0);      //使所有LED灯默认为熄灭状态
}

void InitKey(void)
{
    P0SEL &= ~0x02;     //设置P0.1为普通IO口  
    P0DIR &= ~0x02;     //按键接在P0.1口上，设P0.1为输入模式 
    P0INP &= ~0x02;     //打开P0.1上拉电阻
}

uchar KeyScan(void)
{
    if (KEY1 == 1)
    {
        DelayMS(10);
        if (KEY1 == 1)
        {
          
            return 1;     //有按键按下
        }
    }
    return 0;             //无按键按下
}

void main(void)
{
    InitLed();		      //设置LED1相应的IO口
    InitKey();            //设置S1相应的IO口
    
    while(1)
    {
        if (KeyScan())    //按键按下则改变LED状态
        {
            LED1 = 1;
            LED3 = 0;
            DelayMS(500);
            
            LED1 = 0;
            LED3 = 1;
            DelayMS(500);   
            LedOnOrOff(0);
        }
    }
}
