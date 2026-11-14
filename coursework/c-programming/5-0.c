/*求序列前N项和*/
#include <stdio.h>

int main()
{
	int N;
	scanf("%d", &N);
	
	double sum = 0.0;
	double a = 1.0, b = 2.0;
	double t;
	
	for (int i = 0; i < N; i ++)
	{
		sum += b / a;
		t = a;
		a = b;
		b = b + t;
	}
	
	printf("%.2lf", sum);
	
	return 0;
}