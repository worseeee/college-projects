/*求a的连续和*/
#include <stdio.h>

int main()
{
	int a, n;
	scanf("%d %d", &a, &n);
	
	int sum = 0;
	int t = 0;
	for (int i = 0; i < n; i ++)
	{
		t = 10 * t + a;
		sum += t;
	}
	
	printf("%d\n", sum);
	
	return 0;
}