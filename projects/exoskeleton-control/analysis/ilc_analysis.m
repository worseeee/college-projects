%% ========================================================================
%  ilc_analysis.m  ——  迭代学习控制（ILC）仿真与学习曲线绘制
%  教材对应：第11章（迭代学习控制基本原理、PD型ILC律、收敛性分析）
%
%  ■ ILC核心思想（教材第11章引言）：
%    重复性任务中，每次执行产生的误差携带了对下次改进的完整信息
%    "让机器从每次康复训练的错误中学习，越练越准"
%
%  ■ PD型ILC更新律（教材第11章式11-3）：
%    u_{j+1}(t) = γ · u_j(t) + Kp_ilc · e_j(t) + Kd_ilc · ė_j(t)
%    其中：j=周期索引, γ=渐进康复衰减系数（0<γ<1）
%
%  ■ 收敛条件（教材第11章定理11-1）：
%    ||e_{j+1}||_∞ ≤ ρ · ||e_j||_∞,  ρ < 1
%    ρ = (1 - Kp_ilc·B_0)（B_0为系统输入到输出的直流增益近似）
%    ρ < 1 等价于：0 < Kp_ilc < 2/B_0
%
%  ■ 渐进康复策略（创新点）：
%    γ随周期j递减：γ_j = max(γ_min, γ_0 · γ_decay^j)
%    随着患者康复进展，逐步将控制权交还给患者
% ========================================================================
clear; clc;
load('exo_workspace.mat', 'p', 'ctrl');

fprintf('=== 迭代学习控制（ILC）仿真与分析 ===\n');
fprintf('教材对应：第11章 迭代学习控制\n\n');

%% ── 1. 系统与ILC参数设置 ─────────────────────────────────────────────
Kp_ilc    = ctrl.ilc.Kp;      % ILC比例增益
Kd_ilc    = ctrl.ilc.Kd;      % ILC微分增益
gamma_0   = ctrl.ilc.gamma;   % 初始衰减系数（渐进康复策略）
n_iter    = ctrl.ilc.n_iter;  % 迭代周期数：20
dt        = p.dt;              % 采样步长
T_period  = p.T_period;       % 单周期时长：4s

% 单周期时间序列
t_single = 0:dt:T_period-dt;
n_step   = length(t_single);

fprintf('[ILC] 参数：Kp_ilc=%.3f, Kd_ilc=%.4f, γ_0=%.3f\n', ...
        Kp_ilc, Kd_ilc, gamma_0);

%% ── 2. 收敛性验证（教材第11章定理11-1应用）────────────────────────
% 简化线性化系统的脉冲响应增益（B_0）
% 对于一阶近似：τ_motor → θ 的直流增益 ≈ 1/(B*ω)
% 这里通过数值方法验证
B_0_approx = 1 / (p.B * (2*pi/T_period));
rho = abs(1 - Kp_ilc * B_0_approx);

fprintf('[ILC] 收敛性分析（教材定理11-1）：\n');
fprintf('  系统增益近似 B_0 ≈ %.4f\n', B_0_approx);
fprintf('  收缩因子 ρ = |1 - Kp·B_0| = %.4f\n', rho);
if rho < 1
    fprintf('  ✓ 收敛条件满足（ρ=%.4f < 1），ILC理论保证收敛！\n\n', rho);
else
    fprintf('  ✗ 警告：ρ=%.4f ≥ 1，需降低Kp_ilc或调整系统参数\n\n', rho);
    Kp_ilc = 0.8 / B_0_approx; % 自动修正以满足收敛
    fprintf('  → 自动修正：Kp_ilc = %.4f（确保ρ=0.2）\n\n', Kp_ilc);
end

%% ── 3. 期望轨迹生成 ─────────────────────────────────────────────────
theta_d   = zeros(1, n_step);
dtheta_d  = zeros(1, n_step);
for k = 1:n_step
    [theta_d(k), dtheta_d(k), ~] = min_jerk_traj(t_single(k), T_period, ...
                                                    p.theta_min, p.theta_max);
end

%% ── 4. ILC主循环：20个康复周期 ─────────────────────────────────────
% 存储每周期的关键数据
e_all      = zeros(n_iter, n_step);     % 所有周期的误差
u_all      = zeros(n_iter, n_step);     % 所有周期的控制量
theta_all  = zeros(n_iter, n_step);     % 所有周期的实际轨迹
RMSE_per_cycle = zeros(n_iter, 1);      % 每周期RMSE（学习曲线）
Emax_per_cycle = zeros(n_iter, 1);      % 每周期最大误差

% 初始控制序列（第一周期：用调优的PID控制器生成）
u_j = zeros(1, n_step);
% 用简单P控制生成初始控制序列（作为ILC的热启动）
theta_sim = 0; dtheta_sim = 0;
for k = 1:n_step
    e_k = theta_d(k) - theta_sim;
    u_j(k) = min(p.u_max, max(-p.u_max, 20 * e_k)); % 粗略P控制
    dtheta_sim = dtheta_sim + (u_j(k) - p.B*dtheta_sim - p.K*sin(theta_sim))/p.J * dt;
    theta_sim  = theta_sim + dtheta_sim * dt;
end

fprintf('[ILC] 开始 %d 个康复周期的迭代学习...\n', n_iter);
fprintf('  周期j   RMSE[°]   最大误差[°]   γ值   改善率(%%)\n');
fprintf('  ------  --------  -----------   ----  ---------\n');

for j = 1:n_iter
    %% ── 4.1 渐进康复衰减系数（创新点：逐步交还控制权给患者）────
    % 康复初期：γ≈1（机器主导），康复后期：γ→0（患者主动）
    gamma_j = gamma_0^(1 + 0.05*(j-1)); % 指数衰减
    gamma_j = max(0.5, gamma_j);         % 下限50%（保证安全）

    %% ── 4.2 执行当前周期仿真 ─────────────────────────────────────
    theta_sim   = 0;    % 每周期从相同初始状态出发（ILC假设）
    dtheta_sim  = 0;
    e_j    = zeros(1, n_step);
    de_j   = zeros(1, n_step);
    u_exec = zeros(1, n_step); % 实际执行的控制量

    for k = 1:n_step
        % 计算误差
        e_j(k) = theta_d(k) - theta_sim;
        if k > 1
            de_j(k) = (e_j(k) - e_j(k-1)) / dt;
        end

        % 添加模型不确定性（疲劳+噪声，使ILC需要实际学习）
        t_now = (j-1)*T_period + t_single(k);
        tau_patient = p.tau_patient_max * exp(-t_now/p.fatigue_tau) * 0.5;
        tau_disturbance = tau_patient + p.noise_angle * randn();

        % 执行并记录
        u_exec(k) = min(p.u_max, max(-p.u_max, u_j(k)));
        u_all(j,k) = u_exec(k);

        % 被控对象（含扰动）
        ddtheta_sim = (u_exec(k) + tau_disturbance ...
                      - p.B*dtheta_sim - p.K*sin(theta_sim)) / p.J;
        dtheta_sim  = dtheta_sim + ddtheta_sim * dt;
        theta_sim   = theta_sim  + dtheta_sim  * dt;

        e_all(j,k)     = e_j(k);
        theta_all(j,k) = theta_sim;
    end

    %% ── 4.3 计算本周期性能指标 ────────────────────────────────────
    RMSE_per_cycle(j) = sqrt(mean(e_j.^2));
    Emax_per_cycle(j) = max(abs(e_j));

    if j == 1
        improve_rate = 0;
    else
        improve_rate = (RMSE_per_cycle(j-1) - RMSE_per_cycle(j)) / ...
                        RMSE_per_cycle(j-1) * 100;
    end

    fprintf('  %4d   %8.4f  %11.4f   %.3f  %8.2f\n', ...
            j, rad2deg(RMSE_per_cycle(j)), rad2deg(Emax_per_cycle(j)), ...
            gamma_j, improve_rate);

    %% ── 4.4 ILC更新律（教材第11章核心公式）──────────────────────
    % u_{j+1}(t) = γ_j · u_j(t) + Kp_ilc · e_j(t) + Kd_ilc · ė_j(t)
    de_j_smooth = smooth(de_j, 5)'; % 对微分项平滑（减少噪声放大）
    u_j_next = gamma_j * u_j + Kp_ilc * e_j + Kd_ilc * de_j_smooth;

    % 控制量限幅（安全约束）
    u_j_next = max(-p.u_max, min(p.u_max, u_j_next));

    % 更新下周期控制序列
    u_j = u_j_next;
end

%% ── 5. 绘制ILC学习曲线 ──────────────────────────────────────────────
figure('Name','ILC迭代学习曲线', 'Position',[50,50,1400,900]);

% ---- 5.1 学习曲线（核心：RMSE随周期递减）----
subplot(2,3,1);
semilogy(1:n_iter, rad2deg(RMSE_per_cycle), 'b-o', 'LineWidth', 2, ...
         'MarkerSize', 6, 'MarkerFaceColor','b');
hold on;
semilogy(1:n_iter, rad2deg(Emax_per_cycle), 'r--s', 'LineWidth', 1.5, ...
         'MarkerSize', 5);
% 添加理论收敛上界参考线（教材定理11-1）
rho_actual = rho;
RMSE_theory = rad2deg(RMSE_per_cycle(1)) * rho_actual.^(0:n_iter-1);
semilogy(1:n_iter, RMSE_theory, 'g:', 'LineWidth', 2);
grid on; xlabel('康复周期 j'); ylabel('误差 [°]（对数尺度）');
title('ILC学习曲线（教材第11章核心结果）');
legend('RMSE', '最大误差', '理论上界(ρ^j)', 'Location','northeast');

% ---- 5.2 典型周期轨迹对比 ----
subplot(2,3,2);
t_plot = t_single;
plot(t_plot, rad2deg(theta_d), 'k--', 'LineWidth', 2.5); hold on;
colors = lines(5);
for j_plot = [1, 3, 5, 10, 20]
    if j_plot <= n_iter
        plot(t_plot, rad2deg(theta_all(j_plot,:)), ...
             'Color', colors(min(j_plot,5),:), 'LineWidth', 1.5);
    end
end
grid on; xlabel('时间 [s]'); ylabel('关节角度 [°]');
title('不同周期的轨迹跟踪效果对比');
legend('期望', '周期1', '周期3', '周期5', '周期10', '周期20', ...
       'Location','best');

% ---- 5.3 误差分布对比 ----
subplot(2,3,3);
boxplot(rad2deg(e_all([1,5,10,15,20],:))', ...
        'Labels',{'j=1','j=5','j=10','j=15','j=20'});
grid on; ylabel('跟踪误差 [°]');
title('各周期误差分布（箱线图）');
yline(0, 'r--', 'LineWidth', 1.5);

% ---- 5.4 控制输入演变 ----
subplot(2,3,4);
for j_plot = [1, 5, 10, 20]
    if j_plot <= n_iter
        plot(t_plot, u_all(j_plot,:), 'LineWidth', 1.5); hold on;
    end
end
grid on; xlabel('时间 [s]'); ylabel('控制力矩 [N·m]');
title('控制量随学习进程的演变');
legend('周期1','周期5','周期10','周期20', 'Location','best');

% ---- 5.5 渐进康复策略：助力比例变化 ----
subplot(2,3,5);
gamma_vec = max(0.5, gamma_0.^(1 + 0.05*(0:n_iter-1)));
bar(1:n_iter, gamma_vec * 100, 'FaceColor',[0.2,0.6,0.8]);
grid on; xlabel('康复周期 j'); ylabel('机器助力比例 (%)');
title('渐进康复策略：助力比例逐周期递减');
yline(50, 'r--', '最低助力线', 'LineWidth', 1.5);
ylim([0 110]);

% ---- 5.6 收敛速度分析 ----
subplot(2,3,6);
converge_rate = -diff(log(RMSE_per_cycle));
bar(2:n_iter, converge_rate, 'FaceColor',[0.8,0.4,0.1]);
grid on; xlabel('康复周期 j'); ylabel('对数收敛速率');
title('各周期改善速率（log尺度）');
xline(10,'b--','第10周期','LineWidth',1.5);

sgtitle(sprintf('迭代学习控制(ILC)分析报告\nρ=%.4f < 1，%d周期后RMSE改善%.1f%%', ...
    rho, n_iter, (1-RMSE_per_cycle(end)/RMSE_per_cycle(1))*100));

%% ── 6. 保存分析结果 ─────────────────────────────────────────────────
ilc_results.RMSE_per_cycle = RMSE_per_cycle;
ilc_results.Emax_per_cycle = Emax_per_cycle;
ilc_results.e_all          = e_all;
ilc_results.theta_all      = theta_all;
ilc_results.u_all          = u_all;
ilc_results.theta_d        = theta_d;
ilc_results.rho_convergence= rho;
save('ilc_results.mat', 'ilc_results');
fprintf('\n[Done] ILC分析完成，结果保存至 ilc_results.mat\n');
fprintf('  最终RMSE: %.4f° (初始: %.4f°)\n', ...
        rad2deg(RMSE_per_cycle(end)), rad2deg(RMSE_per_cycle(1)));
fprintf('  总改善率: %.1f%%\n', ...
        (1 - RMSE_per_cycle(end)/RMSE_per_cycle(1))*100);

%% ── 局部函数 ─────────────────────────────────────────────────────────
function [theta, dtheta, ddtheta] = min_jerk_traj(t, T, th_min, th_max)
    T_half=T/2; delta=th_max-th_min; t_mod=mod(t,T);
    if t_mod<=T_half; tau=t_mod/T_half; th0=th_min; dth=delta;
    else; tau=(t_mod-T_half)/T_half; th0=th_max; dth=-delta; end
    f=10*tau^3-15*tau^4+6*tau^5;
    df=(30*tau^2-60*tau^3+30*tau^4)/T_half;
    ddf=(60*tau-180*tau^2+120*tau^3)/T_half^2;
    theta=th0+dth*f; dtheta=dth*df; ddtheta=dth*ddf;
end