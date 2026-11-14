/***************************************************************************
标题：	LCD1602
工作于：LY5A-L2A开发板
作者：	林洋电子-单片机
客服QQ：52927029
网址：	lydz8.taobao.com
******************************************************************************/

#ifndef __LCD1602_H__
#define __LCD1602_H__

/********IO引脚定义***********************************************************/
sbit LCD_RS=P1^0;//定义引脚
sbit LCD_RW=P1^1;
sbit LCD_E=P1^2;

/********宏定义***********************************************************/
#define LCD_Data P0
#define Busy    0x80 //用于检测LCD状态字中的Busy标识

/********函数声明*************************************************************/
void WriteDataLCD(unsigned char WDLCD);					//写数据
void WriteCommandLCD(unsigned char WCLCD,BuysC);		//写命令
unsigned char ReadDataLCD(void);						//读数据
unsigned char ReadStatusLCD(void);						//读状态
void LCDInit(void);										//初始化
void DisplayOneChar(unsigned char X, unsigned char Y, unsigned char DData);			//相应坐标显示字节内容
void DisplayListChar(unsigned char X, unsigned char Y, unsigned char *DData);	//相应坐标开始显示一串内容
void Delay5Ms(void);									//延时
void Delay400Ms(void);									//延时

#endif
