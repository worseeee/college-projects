% --- 1. 定义系统 ---
ts = 0.001; % 采样时间 1ms
G0 = tf(1,[1,3,3,1]); % G(s) = 1/(s³+3s²+3s+1)

% --- 2. 离散化 ---
dsys = c2d(G0,ts,'z'); % 把 G(s) 变成 G(z)
[num,den] = tfdata(dsys,'v'); % 提取 G(z) 的系数

% --- 3. 初始化变量 ---

% 控制器输出历史值
u_1 = 0; % u[k-1]
u_2 = 0; % u[k-2]
u_3 = 0; % u[k-3]

% 系统输出历史值
y_1 = 0; % y[k-1]
y_2 = 0; % y[k-2]
y_3 = 0; % y[k-3]

% 误差历史值
e_1 = 0; % e[k-1]
e_2 = 0; % e[k-2]

% PID 各项值
P_out = 0; % 比例输出
I_out = 0; % 积分输出
D_out = 0; % 微分输出

% PID 参数
kp = 0.5;
ki = 0.01;
kd = 0.005;

% 专家规则参数
M1 = 0.8;
M2 = 0.4;
k1 = 1.5;
k2 = 0.8;
epsilon = 0.01;

% --- 4. 循环 ---

for k = 1:1:1000 % 仿真 1000 步

    % --- 4.1. 定义输入和计算误差 ---
    rin(k) = 1; % 阶跃输入
    yout(k) = -den(2)*y_1 - den(3)*y_2 - den(4)*y_3 + ...
               num(2)*u_1 + num(3)*u_2 + num(4)*u_3;
    e(k) = rin(k) - yout(k);
    
    % --- 4.2. 计算误差变化 ---
    delta_e = e(k) - e_1;
    delta_delta_e = delta_e - (e_1 - e_2);

    % --- 4.3. 专家 PID 规则 ---
    % 规则 (1)
    if abs(e(k)) > M1
        if e(k) > 0
            u(k) = 10; % 最大输出
        else
            u(k) = -10; % 最小输出
        end
    % 规则 (2)
    elseif (e(k) * delta_e > 0) || (delta_e == 0)
        if abs(e(k)) > M2 % 较强控制
            P_out = kp * delta_e;
            I_out = ki * e(k);
            D_out = kd * delta_delta_e / ts;
            u(k) = u_1 + k1 * (P_out + I_out + D_out);
        else % 一般控制
            P_out = kp * delta_e;
            I_out = ki * e(k);
            D_out = kd * delta_delta_e / ts;
            u(k) = u_1 + (P_out + I_out + D_out);
        end
    % 规则 (3)
    elseif (e(k) * delta_e < 0) && ...
           (delta_e * (e_1 - e_2) > 0 || e(k) == 0)
        u(k) = u_1; % 保持不变
    % 规则 (4)
    elseif (e(k) * delta_e < 0) && ...
           (delta_e * (e_1 - e_2) < 0)
        % 找到极值点
        if abs(e(k)) >= M2 % 较强抑制
            u(k) = u_1 + k1*kp*e(k);
        else % 较弱抑制
            u(k) = u_1 + k2*kp*e(k);
        end
    % 规则 (5)
    elseif abs(e(k)) <= epsilon
        % 加入积分
        I_out = I_out + ki * e(k) * ts;
        u(k) = P_out + I_out + D_out;
    end
    
    % --- 4.4. 更新历史值 ---
    u_3 = u_2; u_2 = u_1; u_1 = u(k);
    y_3 = y_2; y_2 = y_1; y_1 = yout(k);
    e_2 = e_1; e_1 = e(k);

end

% --- 5. 画图 ---
time = (1:1000) * ts;
figure;
plot(time,rin,'b--',time,yout,'r-');
legend('Input','Output');
title('Expert PID Step Response');
