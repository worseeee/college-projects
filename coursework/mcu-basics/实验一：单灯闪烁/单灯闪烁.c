#include <regx52.h>
void delay(unsigned int);
void main(void)
{
	while (1)
	{
		P0_7 = 0;
		delay(1000);
		P0_7 = 1;
		delay(2000);
	}
}
void delay(unsigned int n)
{
	unsigned int x,y;
	for (x = 0; x < n; x ++)
  {
    for (y = 0; y < 121; y ++)
    {
      ;
    }
  }
}	