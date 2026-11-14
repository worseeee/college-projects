% --- chap3_3.m ---
clear all;
close all;

% --- 1. 定义论域和隶属函数 ---
x = -3:0.1:3;
mf_params = [-3, -3, -2;   % NB (三角形: a,b,c)
             -3, -2, -1;   % NM
             -2, -1, 0;    % NS
             -1, 0, 1;     % ZE
             0, 1, 2;      % PS
             1, 2, 3;      % PM
             2, 3, 3];   % PB

% --- 2. 绘制隶属函数 ---
figure;
hold on;
for i = 1:7
    y = trimf(x, mf_params(i,:));
    plot(x, y, 'LineWidth', 1.5);
end
title('7个模糊等级的隶属函数');
xlabel('输入值');
ylabel('隶属度');
legend('NB','NM','NS','ZE','PS','PM','PB');
grid on;

% --- 3. 仿真：计算某个输入的隶属度 ---
input_val = -1.5; % 假设输入是 -1.5

% 计算输入值在每个模糊等级下的隶属度
memberships = zeros(1,7);
for i = 1:7
    memberships(i) = trimf(input_val, mf_params(i,:));
end

% --- 4. 显示仿真结果 ---
disp(['输入值为: ', num2str(input_val)]);
disp('对应的隶属度为:');
fuzzy_levels = {'NB', 'NM', 'NS', 'ZE', 'PS', 'PM', 'PB'};
for i = 1:7
    disp([fuzzy_levels{i}, ': ', num2str(memberships(i))]);
end

% 在图上标注输入值
figure(1);
plot([input_val, input_val], [0,1], 'k--', 'LineWidth', 1.5);
text(input_val, 0.5, ['\leftarrow input=', num2str(input_val)], 'FontSize', 12);