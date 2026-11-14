#include <reg51.h>

void delay(unsigned int n)
{
	unsigned int i;
	for(; n > 0; n --)
	  for(i = 0; i < 54; i ++)
	  {
			;
		}
}

unsigned char code LED[8] = {0xfc , 0xf9 , 0xf3 , 0xe7 , 0xcf , 0x9f , 0x3f , 0x7e};
void main(void)
{
	unsigned int i;
	while(1)
	{
		for(i = 0;i < 8; i ++)
		{
			P2 = LED[i];
		  delay(500);
		}
	}
}