% Fuzzy Controller Design (Modern Version)
clear all;
close all;

% 1. 创建 Mamdani 模糊推理系统
a = mamfis('Name', 'fuzzf');

% --- 输入变量 e ---
f1 = 0.1; 
a = addInput(a, [-3*f1, 3*f1], 'Name', 'e');
a = addMF(a, 'e', 'zmf', [-3*f1, -1*f1], 'Name', 'NB');
a = addMF(a, 'e', 'trimf', [-3*f1, -2*f1, 0], 'Name', 'NM');
a = addMF(a, 'e', 'trimf', [-3*f1, -1*f1, 1*f1], 'Name', 'NS');
a = addMF(a, 'e', 'trimf', [-2*f1, 0, 2*f1], 'Name', 'Z');
a = addMF(a, 'e', 'trimf', [-1*f1, 1*f1, 3*f1], 'Name', 'PS');
a = addMF(a, 'e', 'trimf', [0, 2*f1, 3*f1], 'Name', 'PM');
a = addMF(a, 'e', 'smf', [1*f1, 3*f1], 'Name', 'PB');

% --- 输入变量 ec ---
f2 = 0.1;
a = addInput(a, [-3*f2, 3*f2], 'Name', 'ec');
a = addMF(a, 'ec', 'zmf', [-3*f2, -1*f2], 'Name', 'NB');
a = addMF(a, 'ec', 'trimf', [-3*f2, -2*f2, 0], 'Name', 'NM');
a = addMF(a, 'ec', 'trimf', [-3*f2, -1*f2, 1*f2], 'Name', 'NS');
a = addMF(a, 'ec', 'trimf', [-2*f2, 0, 2*f2], 'Name', 'Z');
a = addMF(a, 'ec', 'trimf', [-1*f2, 1*f2, 3*f2], 'Name', 'PS');
a = addMF(a, 'ec', 'trimf', [0, 2*f2, 3*f2], 'Name', 'PM');
a = addMF(a, 'ec', 'smf', [1*f2, 3*f2], 'Name', 'PB');

% --- 输出变量 u ---
f3 = 10;
a = addOutput(a, [-3*f3, 3*f3], 'Name', 'u');
a = addMF(a, 'u', 'zmf', [-3*f3, -1*f3], 'Name', 'NB');
a = addMF(a, 'u', 'trimf', [-3*f3, -2*f3, 0], 'Name', 'NM');
a = addMF(a, 'u', 'trimf', [-3*f3, -1*f3, 1*f3], 'Name', 'NS');
a = addMF(a, 'u', 'trimf', [-2*f3, 0, 2*f3], 'Name', 'Z');
a = addMF(a, 'u', 'trimf', [-1*f3, 1*f3, 3*f3], 'Name', 'PS');
a = addMF(a, 'u', 'trimf', [0, 2*f3, 3*f3], 'Name', 'PM');
a = addMF(a, 'u', 'smf', [1*f3, 3*f3], 'Name', 'PB');

% 2. 编辑规则库 [Input1, Input2, Output1, Weight, Connection]
rulelist=[1 1 1 1 1; 1 2 1 1 1; 1 3 2 1 1; 1 4 2 1 1; 1 5 3 1 1; 1 6 3 1 1; 1 7 4 1 1;
          2 1 1 1 1; 2 2 2 1 1; 2 3 2 1 1; 2 4 3 1 1; 2 5 3 1 1; 2 6 4 1 1; 2 7 5 1 1;
          3 1 2 1 1; 3 2 2 1 1; 3 3 3 1 1; 3 4 3 1 1; 3 5 4 1 1; 3 6 5 1 1; 3 7 5 1 1;
          4 1 2 1 1; 4 2 3 1 1; 4 3 3 1 1; 4 4 4 1 1; 4 5 5 1 1; 4 6 5 1 1; 4 7 6 1 1;
          5 1 3 1 1; 5 2 3 1 1; 5 3 4 1 1; 5 4 5 1 1; 5 5 5 1 1; 5 6 6 1 1; 5 7 6 1 1;
          6 1 3 1 1; 6 2 4 1 1; 6 3 5 1 1; 6 4 5 1 1; 6 5 6 1 1; 6 6 6 1 1; 6 7 7 1 1;
          7 1 4 1 1; 7 2 5 1 1; 7 3 5 1 1; 7 4 6 1 1; 7 5 6 1 1; 7 6 7 1 1; 7 7 7 1 1];
          
a = addRule(a, rulelist);

% 3. 设置解模糊方法并计算查询表
a.DefuzzMethod = 'mom'; % 最大隶属度平均法
writeFIS(a, 'fuzzf');
a2 = readfis('fuzzf');

disp('-------------------------------------------------------');
disp('     fuzzy controller table: e, ec range scaled by f1, f2 ');
disp('-------------------------------------------------------');

Ulist = zeros(7, 7);
% 测试点应在论域范围内，这里使用归一化后的测试值乘以系数
e_test = (-3:1:3) * f1;
ec_test = (-3:1:3) * f2;

for i = 1:7
   for j = 1:7
      % evalfis 现代语法：evalfis(FIS对象, 输入向量)
      Ulist(i,j) = evalfis(a2, [e_test(i), ec_test(j)]);
   end
end

% 输出查询表（向上取整）
Ulist_result = ceil(Ulist)

% 4. 可视化
figure(1); plotfis(a2);
figure(2); plotmf(a2, 'input', 1); title('Input e Membership Functions');
figure(3); plotmf(a2, 'input', 2); title('Input ec Membership Functions');
figure(4); plotmf(a2, 'output', 1); title('Output u Membership Functions');
figure(5); gensurf(a2); title('Control Surface');