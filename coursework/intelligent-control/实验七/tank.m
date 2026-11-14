clc
clear

% 1. 创建 Mamdani 模糊推理系统
fuzz_tank = mamfis('Name', 'fuzz_tank');

% 2. 定义输入变量 'e' (误差)
fuzz_tank = addInput(fuzz_tank, [-3, 3], 'Name', 'e');
fuzz_tank = addMF(fuzz_tank, 'e', 'zmf', [-3, -1], 'Name', 'NB');
fuzz_tank = addMF(fuzz_tank, 'e', 'trimf', [-3, -1, 1], 'Name', 'NS');
fuzz_tank = addMF(fuzz_tank, 'e', 'trimf', [-2, 0, 2], 'Name', 'Z');
fuzz_tank = addMF(fuzz_tank, 'e', 'trimf', [-1, 1, 3], 'Name', 'PS');
fuzz_tank = addMF(fuzz_tank, 'e', 'smf', [1, 3], 'Name', 'PB');

% 3. 定义输出变量 'u' (控制量) (此处修正了原代码中变量名写错的问题)
fuzz_tank = addOutput(fuzz_tank, [-4, 4], 'Name', 'u');
fuzz_tank = addMF(fuzz_tank, 'u', 'zmf', [-4, -1], 'Name', 'NB');
fuzz_tank = addMF(fuzz_tank, 'u', 'trimf', [-4, -2, 1], 'Name', 'NS');
fuzz_tank = addMF(fuzz_tank, 'u', 'trimf', [-2, 0, 2], 'Name', 'Z');
fuzz_tank = addMF(fuzz_tank, 'u', 'trimf', [-1, 2, 4], 'Name', 'PS');
fuzz_tank = addMF(fuzz_tank, 'u', 'smf', [1, 4], 'Name', 'PB');

% 4. 编辑规则库 [输入1 输出1 权重 连接方式(1=AND)]
rulelist = [1 1 1 1;
            2 2 1 1;
            3 3 1 1;
            4 4 1 1;
            5 5 1 1];
fuzz_tank = addRule(fuzz_tank, rulelist);

% 5. 设置解模糊方法并保存 (推荐使用直接赋值方式)
fuzz_tank.DefuzzMethod = 'mom'; % 最大隶属度平均法
writeFIS(fuzz_tank, 'tank');
a2 = readfis('tank');

% 6. 可视化
figure(1); plotfis(a2);
figure(2); plotmf(a2, 'input', 1);
figure(3); plotmf(a2, 'output', 1);

% 7. 规则查看器 (注意：有些版本中 ruleview 需要 fis 文件名或对象)
showrule(a2)
ruleview(a2)

% 8. 生成模糊查询表
disp('-------------------------------------------------------');
disp('      模糊控制器查询表: e=[-3,+3], u=[-4,+4]           ');
disp('-------------------------------------------------------');

e_test = -3:1:3;
Ulist = zeros(1, 7);
for i = 1:7
    % evalfis 的现代语法：evalfis(fis对象, 输入向量)
    Ulist(i) = evalfis(a2, e_test(i));
end

Ulist_rounded = round(Ulist);
disp('输入 e 为 [-3, -2, -1, 0, 1, 2, 3] 时的输出 u 为：');
disp(Ulist_rounded);