/****************************************************************************
* 文 件 名: main.c
* 作    者: Andy
* 修    订: 2013-01-10
* 版    本: 1.0
* 描    述: 继电器接开发板P9座子上，使用P0.5口控制继电器的信息端，
*           高电平继电器断开;低电平继电器吸合，并且继电器吸合指示灯亮 
****************************************************************************/
#include <ioCC2530.h>

typedef unsigned char uchar;
typedef unsigned int  uint;
typedef unsigned long  ulong;

#define LED1    P1_0       // P1.0口控制LED1
#define LED3    P1_4       // P1.4口控制LED3
#define CYCLE   6000
#define UART0_RX    1
#define UART0_TX    2
#define SIZE       51

char RxBuf;
char UartState;
uchar count;
char RxData[SIZE];        //存储发送字符串
/****************************************************************************
* 名    称: DelayMS()
* 功    能: 以毫秒为单位延时 16M时约为535,系统时钟不修改默认为16M
* 入口参数: msec 延时参数，值越大，延时越久
* 出口参数: 无
****************************************************************************/
void DelayMS(uint msec)
{ 
    uint i,j;
    
    for (i=0; i<msec; i++)
        for (j=0; j<535; j++);
}

void Delay(unsigned int t)
{
    while(--t);
}

void InitLed(void)
{
    P1DIR |= 0x11;      //P1.0定义为输出
    LED1 = 0;           //使LED1灯上电默认为熄灭     
    LED3 = 0;
}

void LedEvent(uint bright, int cycle)
{   
    LED1 = 1;               //点亮LED  
    Delay(bright);          //延时,表示LED亮的时间
    LED1 = 0;               //LED熄灭
    Delay(cycle - bright);  //延时,表示LED熄灭的时间
}

void InitUart(void)
{ 
    CLKCONCMD &= ~0x40;      // 设置系统时钟源为 32MHZ晶振
    while(CLKCONSTA & 0x40); // 等待晶振稳定 
    CLKCONCMD &= ~0x47;      // 设置系统主时钟频率为 32MHZ
    
    PERCFG = 0x00;           //外设控制寄存器 USART 0的IO位置:0为P0口位置1 
    P0SEL = 0x0c;            //P0_2,P0_3用作串口（外设功能）
    P2DIR &= ~0xC0;          //P0优先作为UART0
    
    U0CSR |= 0x80;           //设置为UART方式
    U0GCR |= 11;				       
    U0BAUD |= 216;           //波特率设为115200
    UTX0IF = 0;              //UART0 TX中断标志初始置位0
    U0CSR |= 0x40;           //允许接收 
    IEN0 |= 0x84;            //开总中断允许接收中断  
}

void UartSendString(char *Data, int len)
{
    uint i;
    
    for(i=0; i<len; i++)
    {
        U0DBUF = *Data++;
        while(UTX0IF == 0);
        UTX0IF = 0;
    }
}

#pragma vector = URX0_VECTOR 
__interrupt void UART0_ISR(void) 
{ 
    URX0IF = 0;       // 清中断标志 
    RxBuf = U0DBUF;                           
}

void main(void)
{      
    unsigned int j, bright;//定义周期并赋值
    P1DIR |= 0x08;           //P13定义为输出口 
    InitUart();
    InitLed();
    UartState = UART0_RX;                      //串口0默认处于接收模式
    while(1)                 //死循环,继电器间隔3秒开关一次
    {
        if(UartState == UART0_RX)              //接收状态 
        { 
            if(RxBuf != 0) 
            {                 
                if((RxBuf != '#')&&(count < 50))//以'＃'为结束符,一次最多接收50个字符            
                    RxData[count++] = RxBuf; 
                else
                {
                    if(count >= 50)             //判断数据合法性，防止溢出
                    {
                        count = 0;              //计数清0
                        memset(RxData, 0, SIZE);//清空接收缓冲区
                    }
                    else
                    {
                        UartState = UART0_TX;  //进入发送状态
                        if(RxData[0] == 'D' && RxData[1] == '1')
                        {
                            for(bright=1; bright<1000; bright++)
                                LedEvent(bright, 1000);
        
                            LED1 = 1;
                        }
                        if(RxData[0] == 'D' && RxData[1] == '2')
                        {
                            for(bright=1000-1; bright>0; bright--) 
                                LedEvent(bright, 1000);
                        }
                        DelayMS(2000); 
                    }
                }
                RxBuf  = 0;
            }
        }
        
        if(UartState == UART0_TX)              //发送状态 
        {                         
            U0CSR &= ~0x40;                    //禁止接收 
            UartSendString(RxData, count);     //发送已记录的字符串。
            U0CSR |= 0x40;                     //允许接收 
            UartState = UART0_RX;              //恢复到接收状态 
            count = 0;                         //计数清0
            memset(RxData, 0, SIZE);           //清空接收缓冲区
        }    
    }    
}