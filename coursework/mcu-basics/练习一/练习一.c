#include <reg51.h>
#include <intrins.h>
unsigned char code dis_tab[17] = {0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f, 0x77, 0x7c, 0x39, 0x5e, 0x79, 0x71, 0};
unsigned char code LED[8] = {2, 3, 0, 1, 3, 7, 6, 1};
void mdelay(unsigned int delay)
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
unsigned char i, bit_data;
void display_imp()
{
	bit_data = 0xfe;
	for(i = 0; i < 8; i ++)
	{
		P2 = 0xff;
		P1 = dis_tab[LED[i]];
		P2 = bit_data;
		mdelay(5);
		bit_data = _crol_(bit_data , 1);
	}
}
void main()
{
	while(1)
	{
		display_imp();
	}
}