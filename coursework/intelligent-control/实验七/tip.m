clc
clear

% 1. 创建 Mamdani 模糊推理系统对象
tip2 = mamfis('Name', 'tip2'); 

% 2. 添加输入变量 (修改点：使用 Name 参数名)
tip2 = addInput(tip2, [0 10], 'Name', '服务'); 
tip2 = addInput(tip2, [0 10], 'Name', '食物'); 

% 3. 添加输出变量 (修改点：使用 Name 参数名)
tip2 = addOutput(tip2, [0 30], 'Name', '小费'); 

% 4. 添加服务的隶属函数 (注意：函数名大小写 addMF)
tip2 = addMF(tip2, '服务', 'gaussmf', [1.5 0], 'Name', '差');
tip2 = addMF(tip2, '服务', 'gaussmf', [1.5 5], 'Name', '好');
tip2 = addMF(tip2, '服务', 'gaussmf', [1.5 10], 'Name', '很好');

% 5. 添加食物的隶属函数
tip2 = addMF(tip2, '食物', 'trapmf', [0 0 1 3], 'Name', '难吃');
tip2 = addMF(tip2, '食物', 'trimf', [6.8 8.4 10], 'Name', '好吃');

% 6. 添加小费的隶属函数
tip2 = addMF(tip2, '小费', 'trimf', [0 5 10], 'Name', '低');
tip2 = addMF(tip2, '小费', 'trimf', [10 15 20], 'Name', '中');
tip2 = addMF(tip2, '小费', 'trimf', [20 25 30], 'Name', '高');

% 7. 添加规则 (rulelist 逻辑保持不变)
rulelist = [1 1 1 1 1;
            2 1 2 1 1;
            2 2 2 1 1;
            3 2 3 1 1];
tip2 = addRule(tip2, rulelist);

% 8. 显示与可视化
showrule(tip2)

figure(1)
subplot(3,1,1); plotmf(tip2, 'input', 1)
subplot(3,1,2); plotmf(tip2, 'input', 2)
subplot(3,1,3); plotmf(tip2, 'output', 1)

figure(2)
gensurf(tip2) % 产生 FIS 输出曲线