% (1-3) 生成数据
x = rand(1, 100) * 100; % 0-100均匀分布
y1 = x.^2 + sin(x);
y2 = randn(1, 100); % 均值0方差1噪声
y = y1 + y2;

% 数据归一化（关键：因为 y 的值域非常大）
[pn, ps] = mapminmax(x);
[tn, ts] = mapminmax(y);

% (4-5) 使用 logsig
tic;
net1 = newff(minmax(pn), [10, 1], {'logsig', 'logsig'}, 'trainlm'); 
% 注意：如果输出层也用 logsig，tn 必须在 (0,1) 之间
net1 = train(net1, pn, tn);
an1 = sim(net1, pn);
time1 = toc;
mae1 = mae(tn - an1);

% (6) 使用 tansig
tic;
net2 = newff(minmax(pn), [10, 1], {'tansig', 'tansig'}, 'trainlm');
net2 = train(net2, pn, tn);
an2 = sim(net2, pn);
time2 = toc;
mae2 = mae(tn - an2);

fprintf('Logsig: MAE = %f, Time = %fs\n', mae1, time1);
fprintf('Tansig: MAE = %f, Time = %fs\n', mae2, time2);