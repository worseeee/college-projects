/****************************************************************************
* 文 件 名: main.c
* 作    者: Andy
* 修    订: 2013-01-10
* 版    本: 1.0
* 描    述: 将采集到的温湿度通过串口发送到串口调试助手上显示 115200 8N1
****************************************************************************/
#include <ioCC2530.h>
#include <string.h>
#include "UART.H" 
#include "DHT11.H" 

#define UART0_RX    1
#define UART0_TX    2
#define SIZE       51

char RxBuf;
char UartState;
uchar count;
uchar RxData[SIZE];        //存储发送字符串


/****************************************************************************
* 程序入口函数
****************************************************************************/
#pragma vector = URX0_VECTOR 
__interrupt void UART0_ISR(void) 
{ 
    URX0IF = 0;       // 清中断标志 
    RxBuf = U0DBUF;
}


void main(void)
{  
    uchar temp[3]; 
    uchar humidity[3];   
    uchar strTemp[13]="Temperature:";
    uchar strHumidity[10]="Humidity:";
    
    Delay_ms(1000);          //让设备稳定
    InitUart();              //串口初始化
    memset(RxData, 0, SIZE);
    UartState = UART0_RX;
    while(1)
    {         
        if(UartState == UART0_RX)                   //接收状态 
        { 
            if(RxBuf != 0) 
            {                 
                if((RxBuf != '#')&&(count < 50))//以'＃'为结束符,一次最多接收50个字符            
                    RxData[count++] = RxBuf; 
                else
                {
                    if(count >= 50)              //判断数据合法性，防止溢出
                    {
                        count = 0;              //计数清0
                        memset(RxData, 0, SIZE);//清空接收缓冲区
                    }
                    else
                    {
                        UartState = UART0_TX;  //进入发送状态
                        if(RxData[0] == 'D' && RxData[1] == '1')
                        {

        
                            DHT11();             //获取温湿度

                            //将温湿度的转换成字符串
                            temp[0]=wendu_shi+0x30;
                            temp[1]=wendu_ge+0x30;
                            humidity[0]=shidu_shi+0x30;
                            humidity[1]=shidu_ge+0x30;
        
                            //获得的温湿度通过串口输出到电脑显示
                            UartSendString(strTemp, 12);
                            UartSendString(temp, 2);
                            UartSendString("   ", 3);
                            UartSendString(strHumidity, 9);
                            UartSendString(humidity, 2);
                            UartSendString("\n", 1);
                         }
                      }
                   }
                   RxBuf  = 0;
              }
         }
        
        if(UartState == UART0_TX)              //发送状态 
        {                         
            U0CSR &= ~0x40;                  //禁止接收 
            //UartSendString(RxData, count);       //发送已记录的字符串。
            U0CSR |= 0x40;                    //允许接收 
            UartState = UART0_RX;             //恢复到接收状态 
            count = 0;                         //计数清0
            memset(RxData, 0, SIZE);            //清空接收缓冲区
        }    
    }
    
}
