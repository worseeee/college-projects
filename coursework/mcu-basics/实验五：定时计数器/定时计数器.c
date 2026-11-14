#include <reg52.h>
sbit LED = P0^0;
unsigned char cnt = 0;
void main()
{
	TMOD = 0x01;
	TH0 = (65536 - 50000) / 256;
	TL0 = (65536 - 50000) % 256;
	EA = 1;
	ET0 = 1;
	TR0 = 1;
	while(1)
	{
		;
	}
}
void T0_int() interrupt 1
{
	TH0 = (65536 - 50000) / 256;
	TL0 = (65536 - 50000) % 256;
  cnt ++;
	if(cnt == 20)
	{
		cnt = 0;
		LED = !LED;
	}
}