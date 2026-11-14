/*约分最简分式*/
#include <stdio.h>

int main()
{
	int a, b;
	scanf("%d/%d", &a, &b);
	
	int t;
	int m = a, n = b;
	while (n != 0)
	{
		t = m % n;
		m = n;
		n = t;
	}
	
	a /= m;
	b /= m;
	
	printf("%d/%d", a, b);
	
	return 0;
}