#include <reg51.h>

void delay(unsigned int n)
{
	unsigned int i;
	for(; n > 0; n --)
	  for(i = 0; i < 100; i ++)
	  {
			;
		}
}

sbit LED0 = P1^0;
sbit LED1 = P1^1;
sbit LED2 = P1^2;
sbit LED3 = P1^3;
sbit LED4 = P1^4;
sbit LED5 = P1^5;
sbit key = P3^2;
void ext0_init()
{
	IT0 = 0;
	EX0 = 1;
	EA = 1;
	PX0 = 0;
}
void main()
{
	ext0_init();
	while(1)
	{
	  LED0 = 0;
		LED1 = 0;
		LED2 = 0;
		LED3 = 0;
	  LED4 = 0;
		LED5 = 0;
		delay(250);
	  LED0 = 1;
		LED1 = 1;
		LED2 = 1;
		LED3 = 1;
	  LED4 = 1;
		LED5 = 1;
		delay(250);
	}
}
void ext0() interrupt 0
{
	LED0 = 0;
	LED1 = 0;
	LED2 = 0;
	LED3 = 0;
	LED4 = 0;
	LED5 = 0;
	delay(1000);
  LED0 = 1;
	LED1 = 1;
	LED2 = 1;
	LED3 = 1;
	LED4 = 1;
  LED5 = 1;
	delay(1000);
}