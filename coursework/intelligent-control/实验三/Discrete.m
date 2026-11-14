clear all;
close all; 
ts=0.001;
sys=tf(523500,[1,87.35,10470,0]);
dsys=c2d(sys,ts,'z');
[num,den]=tfdata(dsys,'v'); 
u_1=0.0;u_2=0.0;u_3=0.0;
y_1=0.0;y_2=0.0;y_3=0.0;
x=[0,0,0]';
error_1=0;
for k=1:1:500
time(k)=k*ts;   
S=3;
if S==1
    kp=0.50;ki=0.001;kd=0.001;          
    rin(k)=1;                       %Step Signal
elseif S==2
    kp=0.50;ki=0.001;kd=0.001;          
    rin(k)=sign(sin(2*2*pi*k*ts));  %Square Wave Signal
elseif S==3
    kp=1.5;ki=1.0;kd=0.01;          %Sine Signal
    rin(k)=0.5*sin(2*2*pi*k*ts);           
end 
u(k)=kp*x(1)+kd*x(2)+ki*x(3);    %PID Controller
%Restricting the output of controller
if u(k)>=10       
   u(k)=10;
end
if u(k)<=-10
   u(k)=-10;
end
%Linear model
yout(k)=-den(2)*y_1-den(3)*y_2-den(4)*y_3+num(2)*u_1+num(3)*u_2+num(4)*u_3; 
error(k)=rin(k)-yout(k);
%Return of parameters
u_3=u_2;u_2=u_1;u_1=u(k);
y_3=y_2;y_2=y_1;y_1=yout(k);   
x(1)=error(k);                %Calculating P
x(2)=(error(k)-error_1)/ts;   %Calculating D
x(3)=x(3)+error(k)*ts;        %Calculating I 
error_1=error(k);
end
figure(1);
plot(time,rin,'b',time,yout,'r');
xlabel('time(s)'),ylabel('rin,yout'); 
figure(2);
plot(time,error,'r')
xlabel('time(s)');ylabel('error');