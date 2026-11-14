G0=tf(1,[1,3,3,1]); 
P=[0.1 0.3  0.5 1 2 3];
figure, 	hold on
for i=1:length(P)
   G=feedback(P(i)*G0,1);
   step(G);   %阶跃响应 
  pause(1);
end
