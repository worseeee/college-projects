#ifndef __UART_H__
#define __UART_H__

extern void InitUart();   //初始化串口
extern void UartSendString(unsigned char *Data,int len);

#endif