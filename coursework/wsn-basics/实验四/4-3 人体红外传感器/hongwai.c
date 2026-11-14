#include "ioCC2530.h"      // 申明该文件中用到的头文件
typedef unsigned int  uint;
typedef unsigned char  uchar;
void UartSendString(uchar *Data, int len)
{
    uint i;
    
    for(i=0; i<len; i++)
    {
        U0DBUF = *Data++;
        while(UTX0IF == 0);
        UTX0IF = 0;
    }
}

void InitUart(void)
{ 
    PERCFG = 0x00;           //外设控制寄存器 USART 0的IO位置:0为P0口位置1 
    P0SEL = 0x0c;            //P0_2,P0_3用作串口（外设功能）
    P2DIR &= ~0XC0;          //P0优先作为UART0
    
    U0CSR |= 0x80;           //设置为UART方式
    U0GCR |= 11;				       
    U0BAUD |= 216;           //波特率设为115200
    UTX0IF = 0;              //UART0 TX中断标志初始置位0
}

void main( void )
{
  CLKCONCMD &= ~0x40;               //设置系统时钟源为32MHZ晶振
  while(CLKCONSTA & 0x40);          //等待晶振稳定为32M
  CLKCONCMD &= ~0x47;               //设置系统主时钟频率为32MHZ  
  
  InitUart();   
  P0DIR &= ~0x20;  
  P1DIR |= 0x11;  
  
    P1_0 = 0;

    P1_4 = 0;

  
  while(1)
  {
     uchar str[8]="Warning";
     
     if(P0_5 == 1)
     {
      P1_0 = 1;
      UartSendString(str, 7);
     }
     
     
     if(P0_5 == 0)
       P1_0 = 0;

  }
} // end of main()