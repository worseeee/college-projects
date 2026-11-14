/*然后是几点*/
#include <stdio.h>

int main()
{
	int t1 = 0;
	int t2 = 0;
	
	scanf("%d %d", &t1, &t2);
	
	int t1_min = t1 / 100 * 60 + t1 % 100;
	int t_min = t1_min + t2;
	int t = t_min / 60 * 100 + t_min % 60;
	
	printf("%d\n", t);
	
	return 0;
}