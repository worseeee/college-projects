/*打印九九口诀表*/
#include <stdio.h>

int main()
{
	int N;
	
	scanf("%d", &N);
	
	int i = 1;
	
	while (i <= N)
	{
		int j = 1;
		
		while (j <= i)
		{
			printf("%d*%d=%d  ", j, i, j * i);
			
			if (i * j < 10)
			{
				printf("   ");
			}
			else
			{
				printf("  ");
			}
			
			j ++;
		}
		
		printf("\n");
		i ++;
	}
	
	return 0;
}