/*超速判断*/
#include <stdio.h>

int main()
{
	int v = 0;
	
	scanf("%d", &v);
	
	if (v > 60)
	{
		printf("Speed: %d - Speeding\n", v);
	}
	else
	{
		printf("Speed: %d - OK\n", v);
	}
	
	return 0;
}