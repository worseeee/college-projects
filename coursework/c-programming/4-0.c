/*求符合给定条件的整数集*/
#include <stdio.h>

int main()
{
	int i, j, k, num, lim;
	int cnt = 0;
	
	scanf("%d", &num);
	
	lim = num + 3;
	
	i = num;
	while (i <= lim)
	{
		j = num;
		while (j <= lim)
		{
			k = num;
			while (k <= lim)
			{
				if (i != j && i != k && j != k)
				{
					printf("%d ", i * 100 + j * 10 + k);
					cnt ++;
					
					if (cnt % 6 == 0)
					{
						printf("\n");
					}
				}
				k ++;
			}
			j ++;
		}
		i ++;
	}
	
	return 0;
}