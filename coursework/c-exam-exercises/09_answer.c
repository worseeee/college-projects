#include <stdio.h>
int main()
{
   int a1,a2,b1,b2;
   do
      scanf("%d%d",&a1,&a2);
   while(a1<0 || a1>12 || a2<0 || a2>31);
   do
      scanf("%d%d",&b1,&b2);
   while(b1<0 || b1>12 || b2<0 || b2>31);
    
   if(a1<b1) printf("%d %d",a1,a2);
   else
      if(a1==b1 && a2<b2) printf("%d %d",a1,a2);
      else printf("%d %d",b1,b2);
}
