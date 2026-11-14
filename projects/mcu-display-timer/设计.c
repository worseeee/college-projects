#include <reg52.h>

sbit LCD_RS=P1^0;
sbit LCD_RW=P1^1;
sbit LCD_E=P1^2;

#define LCD_Data P0
#define Busy    0x80 

unsigned char code uctech[] = {"liushengwei"};
unsigned char code id[] = {"0000000000"};
unsigned char second = 0; 
unsigned char second_str[3] = "00"; 

void WriteDataLCD(unsigned char WDLCD);					
void WriteCommandLCD(unsigned char WCLCD,BuysC);		
unsigned char ReadDataLCD(void);						
unsigned char ReadStatusLCD(void);						
void LCDInit(void);								
void DisplayOneChar(unsigned char X, unsigned char Y, unsigned char DData);			
void DisplayListChar(unsigned char X, unsigned char Y, unsigned char code *DData);	
void DisplayListChar1(unsigned char X, unsigned char Y, unsigned char data *DData);	
void Delay5Ms(void);							
void Delay400Ms(void);						
void Timer0Init(void);									
void UpdateSecondDisplay(void);							
	
void main(void)
{
	Delay400Ms(); 	
	LCDInit(); 		
	Delay5Ms(); 	
	
	DisplayListChar(0, 0, uctech);  
	DisplayListChar(0, 1, id);      
	
	Timer0Init();    // ??????
	
	EA = 1;          // ????
	ET0 = 1;         // ????0??
	
	while(1);
}

/***********???0???********************************************************/
void Timer0Init(void)
{
	TMOD = 0x01;    // ?????0???1(16????)
	TH0 = 0x3C;     // ????,??50ms
	TL0 = 0xB0;
	TR0 = 1;        // ?????0
}

/***********???0??????********************************************************/
void Timer0_ISR(void) interrupt 1
{
	static unsigned char count = 0;
	
	TH0 = 0x3C;     // ??????
	TL0 = 0xB0;
	
	count++;
	if(count >= 20) // 50ms * 20 = 1s
	{
		count = 0;
		second++;
		if(second >= 60)
		{
			second = 0;
		}
		
		// ?????
		second_str[0] = '0' + second / 10;
		second_str[1] = '0' + second % 10;
		UpdateSecondDisplay();
	}
}

/***********?????********************************************************/
void UpdateSecondDisplay(void)
{
	DisplayOneChar(10, 1, second_str[0]);  // ??????????
	DisplayOneChar(11, 1, second_str[1]);  // ??????????
}

/***********???********************************************************/	
void WriteDataLCD(unsigned char WDLCD)
{
 	ReadStatusLCD(); //???
 	LCD_Data = WDLCD;
 	LCD_RS = 1;
 	LCD_RW = 0;
 	LCD_E = 0; 		//??????????????????
 	LCD_E = 0; 		//??
 	LCD_E = 1;
}

/***********???********************************************************/	
void WriteCommandLCD(unsigned char WCLCD,BuysC) //BuysC?0??????
{
 	if (BuysC) ReadStatusLCD(); //???????
 	LCD_Data = WCLCD;
 	LCD_RS = 0;
 	LCD_RW = 0; 
 	LCD_E = 0;
 	LCD_E = 0;
	LCD_E = 1; 
}

/***********???********************************************************/	
unsigned char ReadDataLCD(void)
{
 	LCD_RS = 1; 
 	LCD_RW = 1;
 	LCD_E = 0;
 	LCD_E = 0;
 	LCD_E = 1;
 	return(LCD_Data);
}

/***********???*******************************************************/	
unsigned char ReadStatusLCD(void)
{
 	LCD_Data = 0xFF; 
 	LCD_RS = 0;
 	LCD_RW = 1;
 	LCD_E = 0;
 	LCD_E = 0;
 	LCD_E = 1;
 	while (LCD_Data & Busy); //?????
 	return(LCD_Data);
}

/***********???********************************************************/	
void LCDInit(void)
{
 	LCD_Data = 0;
 	WriteCommandLCD(0x38,0); 	//??????,??????
 	Delay5Ms(); 
 	WriteCommandLCD(0x38,0);
 	Delay5Ms(); 
 	WriteCommandLCD(0x38,0);
 	Delay5Ms(); 

 	WriteCommandLCD(0x38,1); 	//??????,???????????
 	WriteCommandLCD(0x08,1); 	//????
 	WriteCommandLCD(0x01,1); 	//????
 	WriteCommandLCD(0x06,1); 	//????????
 	WriteCommandLCD(0x0C,1); 	//????????
}

/***********???????????*******************************************/	
void DisplayListChar1(unsigned char X, unsigned char Y, unsigned char data *DData)	//????????????
{
 	Y &= 0x1;
 	X &= 0xF; 				//??X????15,Y????1
 	if (Y) X |= 0x40; 		//???????????+0x40;
 	X |= 0x80; 			//?????
 	WriteCommandLCD(X, 0); //????????,?????
 	WriteDataLCD(DData);
}
void DisplayOneChar(unsigned char X, unsigned char Y, unsigned char DData)
{
 	Y &= 0x1;
 	X &= 0xF; 				//??X????15,Y????1
 	if (Y) X |= 0x40; 		//???????????+0x40;
 	X |= 0x80; 			//?????
 	WriteCommandLCD(X, 0); //????????,?????
 	WriteDataLCD(DData);
}
void DisplayOneChar1(unsigned char X, unsigned char Y, unsigned char DData)
{
 	Y &= 0x1;
 	X &= 0xF; 				//??X????15,Y????1
 	if (Y) X |= 0x40; 		//???????????+0x40;
 	X |= 0x80; 			//?????
 	WriteCommandLCD(X, 0); //????????,?????
 	WriteDataLCD(DData);
}
/***********???????????*****************************************/	
void DisplayListChar(unsigned char X, unsigned char Y, unsigned char code *DData)
{
 	unsigned char ListLength;

 	ListLength = 0;
 	Y &= 0x1;
 	X &= 0xF; 				//??X????15,Y????1
 	while (DData[ListLength]>=0x20){ //??????????
   		if (X <= 0xF){ 		//X?????0xF
     		DisplayOneChar(X, Y, DData[ListLength]); //??????
     		ListLength++;
     		X++;
    	}
  	}
}

/***********???********************************************************/	
void Delay5Ms(void)
{
 	unsigned int TempCyc = 5552;
 	while(TempCyc--);
}

/***********???********************************************************/	
void Delay400Ms(void)
{
 	unsigned char TempCycA = 5;
 	unsigned int TempCycB;
 	while(TempCycA--){
  		TempCycB=7269;
  		while(TempCycB--);
 	}
}
