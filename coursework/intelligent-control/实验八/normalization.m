x = 0:.1:10;
y = 0.12*exp(-0.213*x) + 0.54*exp(-0.17*x).*sin(1.23*x);

% 提示：对于 x 范围较大的数据，使用 mapminmax 进行归一化
[pn, ps] = mapminmax(x);
[tn, ts] = mapminmax(y);

net = newff(minmax(pn), [10, 1], {'tansig', 'purelin'});
net = train(net, pn, tn);
an = sim(net, pn);
a = mapminmax('reverse', an, ts); % 反归一化得到真实值

plot(x, y, 'b', x, a, 'r--');