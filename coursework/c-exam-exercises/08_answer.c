#include <stdio.h>
int main()
{
   float x,y;
   do
      scanf("%f%f",&x,&y);
   while(x<=0 || y<=0);
   
   if(x/(y*y)>25) printf("fat");
   else if(x/(y*y)<19) printf("thin");  
   else printf("good");    
}
