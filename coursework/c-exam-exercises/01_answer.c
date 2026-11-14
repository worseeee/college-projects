#include <stdio.h>
#define N 10
int main()
{
   double a[N], v=0, s=0;
   int i;
   
   for(i=0; i<N; i++){
   	  scanf("%lf",&a[i]);
      v=v+a[i]/N;
   }
      
      
   for(i=0; i<N; i++)
	  if(a[i]>=v) s=s+a[i];
	  
   printf("%f %f\n",v,s);
}