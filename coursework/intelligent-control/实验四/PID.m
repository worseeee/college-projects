% --- 1. 系统定义 ---
clear all; close all;
ts = 0.001; % 采样时间 1ms
Gp = tf(133, [1, 25, 0]); % Gp(s) = 133 / (s² + 25s)
dGp = c2d(Gp, ts, 'z');
[num, den] = tfdata(dGp, 'v');

% --- 2. 传统 PID ---
u_trad_1 = 0; u_trad_2 = 0;
y_trad_1 = 0; y_trad_2 = 0;
error_trad_1 = 0; I_out_trad = 0;
kp_trad = 0.5; ki_trad = 0.2; kd_trad = 0.1;
for k = 1:1:2000
    time(k) = k * ts;
    rin(k) = 1;
    yout_trad(k) = -den(2)*y_trad_1 - den(3)*y_trad_2 + num(2)*u_trad_1 + num(3)*u_trad_2;
    error_trad(k) = rin(k) - yout_trad(k);
    P_out_trad = kp_trad * error_trad(k);
    I_out_trad = I_out_trad + ki_trad * error_trad(k) * ts;
    D_out_trad = kd_trad * (error_trad(k) - error_trad_1) / ts;
    u_trad(k) = P_out_trad + I_out_trad + D_out_trad;
    u_trad_2 = u_trad_1; u_trad_1 = u_trad(k);
    y_trad_2 = y_trad_1; y_trad_1 = yout_trad(k);
    error_trad_1 = error_trad(k);
end

% --- 3. 专家 PID  ---
u_exp_1 = 0; u_exp_2 = 0;
y_exp_1 = 0; y_exp_2 = 0;
e_exp_1 = 0; e_exp_2 = 0; I_out_exp = 0;
kp_exp = 0.5; ki_exp = 0.2; kd_exp = 0.1;
M1 = 0.5; M2 = 0.2;
k1 = 1.5; k2 = 0.8;
epsilon = 0.05; % ← 适当放大死区，避免边界抖动

for k = 1:1:2000
    yout_exp(k) = -den(2)*y_exp_1 - den(3)*y_exp_2 + num(2)*u_exp_1 + num(3)*u_exp_2;
    e_exp(k) = rin(k) - yout_exp(k);
    delta_e = e_exp(k) - e_exp_1;
    delta_delta_e = delta_e - (e_exp_1 - e_exp_2);

    % ★ 修改1：epsilon 精细控制优先级最高，移到最前
    if abs(e_exp(k)) <= epsilon
        I_out_exp = I_out_exp + ki_exp * e_exp(k) * ts;
        u_exp(k) = kp_exp*e_exp(k) + I_out_exp + kd_exp*delta_e/ts;
        % ↑ 修改3：微分用 delta_e/ts（位置式），去掉二阶差分

    % ★ 修改2：Bang-bang 幅值从10降为5，减缓冲击
    elseif abs(e_exp(k)) > M1
        u_exp(k) = 5 * sign(e_exp(k));

    elseif (e_exp(k) * delta_e > 0) || (delta_e == 0)
        % 误差在增大：加速调节
        u_exp(k) = u_exp_1 + k1*(kp_exp*delta_e + ki_exp*e_exp(k)*ts + kd_exp*delta_delta_e);
        % ↑ 修改3：去掉 /ts，delta_delta_e 不再被放大1000倍

    elseif (e_exp(k) * delta_e < 0) && (delta_e * (e_exp_1 - e_exp_2) > 0 || e_exp(k) == 0)
        % 误差在减小且仍在远离目标：保持
        u_exp(k) = u_exp_1;

    elseif (e_exp(k) * delta_e < 0) && (delta_e * (e_exp_1 - e_exp_2) < 0)
        % 误差过了极值点：比例修正
        if abs(e_exp(k)) >= M2
            u_exp(k) = u_exp_1 + k1*kp_exp*e_exp(k);
        else
            u_exp(k) = u_exp_1 + k2*kp_exp*e_exp(k);
        end

    else
        u_exp(k) = u_exp_1 + kp_exp*delta_e + ki_exp*e_exp(k)*ts + kd_exp*delta_delta_e;
    end

    if u_exp(k) > 10, u_exp(k) = 10; end
    if u_exp(k) < -10, u_exp(k) = -10; end

    u_exp_2 = u_exp_1; u_exp_1 = u_exp(k);
    y_exp_2 = y_exp_1; y_exp_1 = yout_exp(k);
    e_exp_2 = e_exp_1; e_exp_1 = e_exp(k);
end

% --- 4. 绘图对比 ---
figure;
plot(time, rin, 'k--', 'LineWidth', 1.5); hold on;
plot(time, yout_trad, 'b-', 'LineWidth', 1.5);
plot(time, yout_exp, 'r-', 'LineWidth', 1.5);
grid on;
xlabel('Time (s)'); ylabel('Amplitude');
title('Comparison of Traditional PID and Expert PID');
legend('Input', 'Traditional PID', 'Expert PID');
axis([0 2 0 1.5]);
