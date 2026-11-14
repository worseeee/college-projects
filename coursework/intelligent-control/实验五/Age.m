% --- 3-1: 隶属函数仿真 ---
clear all;
close all;

% --- 1. 定义论域 ---
a = 0:1:200; % 年龄从0到200

% --- 2. 计算四个隶属函数 ---
mu_O = zeros(size(a));
mu_Y = zeros(size(a));

for i = 1:length(a)
    age = a(i);
    % 老 O
    if age >= 50 && age <= 70
        mu_O(i) = (age - 50) / 20;
    elseif age > 70
        mu_O(i) = 1.0;
    end
    
    % 年轻 Y
    if age >= 0 && age <= 25
        mu_Y(i) = 1.0;
    elseif age > 25 && age <= 70
        mu_Y(i) = (70 - age) / 45;
    end
end

% 很年轻 W = Y²
mu_W = mu_Y.^2;

% 不老也不年轻 V = min(1-O, 1-Y)
mu_V = min(1 - mu_O, 1 - mu_Y);

% --- 3. 绘图 ---
figure;
plot(a, mu_O, 'r-', 'LineWidth', 2); hold on;
plot(a, mu_Y, 'g-', 'LineWidth', 2);
plot(a, mu_W, 'b--', 'LineWidth', 2);
plot(a, mu_V, 'm-.', 'LineWidth', 2);
grid on;
title('四种年龄隶属函数');
xlabel('年龄 (a)');
ylabel('隶属度');
legend('老 O', '年轻 Y', '很年轻 W', '不老也不年轻 V');
axis([0 200 -0.1 1.1]);
