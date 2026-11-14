#include <reg51.h>
#include <intrins.h>
unsigned char code dis_tab[17] = {0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f, 0x77, 0x7c, 0x39, 0x5e, 0x79, 0x71, 0};
unsigned char LED[8];
void delay(unsigned int delay)
{
	unsigned int i;
	for(; delay > 0; delay --)
	{
		for(i = 0; i < 114; i ++)
		{
			;
		}
	}
}
unsigned char i, bit_data, second, cnt;
void display_imp()
{
	LED[0] = second % 10;
	LED[1] = second % 100 / 10;
	LED[2] = second / 100;
	bit_data = 0xfe;
  for(i = 0; i < 8; i ++)
	{
	P0 = 0xff;
	P1 = dis_tab[LED[i]];
	P0 = bit_data;
	bit_data = _crol_(bit_data , 1);
	}
}
void main()
{
	TMOD = 0x01;
	TH0 = (65536 - 50000) / 256;
	TL0 = (65536 - 50000) % 256;
	ET0 = 1;
	EA = 1;
	TR0 = 1;
	TR1 = 1;
	LED[3] = 16;
	LED[4] = 0;
	LED[5] = 0;
	LED[6] = 1;
	LED[7] = 1;
	while(1)
	{
		display_imp();
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
		second ++;
	}
}
