#include <stdio.h>
#include <math.h>
int main()
{
   int a,b,c;
   do
     scanf("%d%d%d",&a,&b,&c);
   while(a==0);
   if(sqrt(b*b-4*a*c)>0) printf("2");
   else
      if(sqrt(b*b-4*a*c)==0) printf("1");
      else printf("0");
   return 0;
}
/*
if(sqrt(b*b-4*a*c)>0) printf("2");
if(sqrt(b*b-4*a*c)==0) printf("1");
if(sqrt(b*b-4*a*c)<0) printf("0");
*/

