%% ========================================================================
%  compare_results.m  ——  六层控制器横向对比分析与报告绘图
%  教材对应：贯穿全书（第1-11章知识的综合对比体现）
%  实验对应：实验一（MATLAB绘图技能）、实验三（PID vs 专家PID对比）
%
%  ■ 本脚本功能：
%    1. 对六层控制器在三种工况下进行完整MATLAB仿真（不需要Simulink）
%    2. 计算七项性能评估指标
%    3. 生成专业对比图表（可直接用于课程报告）
% ========================================================================
clear; clc;
load('exo_workspace.mat', 'p', 'ctrl');

fprintf('=== 六层控制器横向对比分析 ===\n');
fprintf('三种工况：正常 / 肌肉疲劳 / 痉挛脉冲\n\n');

%% ── 仿真设置 ─────────────────────────────────────────────────────────
dt       = p.dt;          % 1ms
T_sim    = 20.0;          % 仿真20秒（含5个完整康复周期）
t_vec    = 0:dt:T_sim-dt;
n_step   = length(t_vec);

% 期望轨迹
theta_d   = zeros(1, n_step);
dtheta_d  = zeros(1, n_step);
for k = 1:n_step
    [theta_d(k), dtheta_d(k), ~] = min_jerk_traj(t_vec(k), ...
                                     p.T_period, p.theta_min, p.theta_max);
end

% 三种工况设置
scenarios = {'normal', 'fatigue', 'spasm'};
scenario_names = {'正常工况', '肌肉疲劳', '痉挛脉冲'};
n_scenario = 3;
n_layer    = 6;
layer_names = {'L1-基准PID', 'L2-专家PID', 'L3-模糊PID', ...
               'L4-RBF自适应', 'L5-PSO优化', 'L6-ILC'};

%% ── 存储所有结果 ────────────────────────────────────────────────────
theta_all = zeros(n_layer, n_scenario, n_step);
u_all     = zeros(n_layer, n_scenario, n_step);

% 性能指标矩阵
RMSE       = zeros(n_layer, n_scenario);
PeakError  = zeros(n_layer, n_scenario);
Overshoot  = zeros(n_layer, n_scenario);
Energy     = zeros(n_layer, n_scenario);
SettleTime = zeros(n_layer, n_scenario); % 进入±2°带的时间

%% ── 仿真主循环：六层 × 三工况 ──────────────────────────────────────
fprintf('运行仿真矩阵（6×3=18组）...\n');

for sc = 1:n_scenario
    for ly = 1:n_layer
        fprintf('  Layer %d, 工况[%s]...', ly, scenario_names{sc});

        % 初始化被控对象状态
        theta_sim  = 0;
        dtheta_sim = 0;

        % 初始化控制器状态
        e_int  = 0;   % PID积分项
        e_prev = 0;   % 上一时刻误差
        u_prev = 0;   % 上一时刻控制量
        e_prev2= 0;   % 上上时刻误差
        I_term = 0;   % 专家PID积分项

        theta_rec = zeros(1, n_step);
        u_rec     = zeros(1, n_step);

        for k = 1:n_step
            t = t_vec(k);

            % ---- 计算误差 ----
            e    = theta_d(k) - theta_sim;
            de   = (e - e_prev) / dt;

            % ---- 根据控制层次计算控制量 ----
            switch ly
                case 1  % 基准PID
                    e_int = e_int + e * dt;
                    u = ctrl.pid.Kp*e + ctrl.pid.Ki*e_int + ctrl.pid.Kd*de;

                case 2  % 专家PID（简化版，完整版见expert_pid_sfunc.m）
                    [u, u_prev, I_term, e_prev2] = expert_pid_step(...
                        e, de, u_prev, I_term, e_prev2, e_prev, ctrl.expert, dt);
                    u_prev_raw = u; % 记录用于下一步

                case 3  % 模糊PID（使用FIS评估，需先运行design_fis.m）
                    if exist('knee_fuzzy_pid.fis','file')
                        fis = readfis('knee_fuzzy_pid.fis');
                        delta_params = evalfis(fis, [e, de]);
                        Kp_t = max(0.1, ctrl.fuzzy.Kp_base + delta_params(1));
                        Ki_t = max(0.0, ctrl.fuzzy.Ki_base + delta_params(2));
                        Kd_t = max(0.0, ctrl.fuzzy.Kd_base + delta_params(3));
                    else % 若FIS文件不存在，用自适应参数估算
                        Kp_t = ctrl.pid.Kp * (1 + 0.3*tanh(abs(e)/0.1));
                        Ki_t = ctrl.pid.Ki * (1 - 0.5*tanh(abs(e)/0.05));
                        Kd_t = ctrl.pid.Kd * (1 + 0.2*tanh(abs(de)/0.1));
                    end
                    e_int = e_int + e * dt;
                    u = Kp_t*e + Ki_t*e_int + Kd_t*de;

                case 4  % RBF自适应（简化：用自适应增益近似）
                    % 完整版见rbf_controller_sfunc.m
                    % 这里用近似：不确定性补偿 ≈ 15% 误差额外修正
                    e_int = e_int + e * dt;
                    u_pid = ctrl.pid.Kp*e + ctrl.pid.Ki*e_int + ctrl.pid.Kd*de;
                    % RBF补偿：基于当前状态的自适应修正
                    u_rbf = 0.8 * sign(e) * min(abs(e)*50, p.u_max*0.3);
                    u = u_pid + u_rbf;

                case 5  % PSO优化参数（与L3相同结构，参数来自PSO结果）
                    if isfield(ctrl,'pso') && isfield(ctrl.pso,'best_params')
                        best = ctrl.pso.best_params;
                        Kp_t = best(1); Ki_t = best(2); Kd_t = best(3);
                    else
                        Kp_t = ctrl.pid.Kp * 1.2;
                        Ki_t = ctrl.pid.Ki * 0.9;
                        Kd_t = ctrl.pid.Kd * 1.1;
                    end
                    e_int = e_int + e * dt;
                    u = Kp_t*e + Ki_t*e_int + Kd_t*de;

                case 6  % ILC（使用来自ilc_analysis.m的前馈序列）
                    if exist('ilc_results.mat','file')
                        ilc = load('ilc_results.mat');
                        k_safe = min(k, length(ilc.ilc_results.u_all(end,:)));
                        u_ilc_ff = ilc.ilc_results.u_all(end, k_safe);
                    else
                        u_ilc_ff = 0; % 若ILC未运行，用零前馈
                    end
                    % ILC = 前馈（学习得到） + 反馈PID
                    e_int = e_int + e * dt;
                    u_fb = ctrl.pid.Kp*e + ctrl.pid.Ki*e_int + ctrl.pid.Kd*de;
                    u = u_ilc_ff * 0.8 + u_fb;
            end

            % ---- 工况扰动注入 ----
            switch sc
                case 1  % 正常工况：无额外扰动
                    tau_disturbance = p.noise_angle * randn();
                case 2  % 肌肉疲劳：患者力矩随时间衰减
                    tau_patient = p.tau_patient_max * exp(-t/p.fatigue_tau) * ...
                                  abs(sin(pi*t/p.T_period));
                    tau_disturbance = tau_patient + p.noise_angle * randn();
                case 3  % 痉挛脉冲：周期性高幅值扰动
                    spasm_t = mod(t, p.spasm_interval);
                    if spasm_t < p.spasm_duration
                        tau_spasm = p.spasm_amp;
                    else
                        tau_spasm = 0;
                    end
                    tau_disturbance = tau_spasm + p.noise_angle * randn();
            end

            % ---- 控制量限幅 ----
            u = max(-p.u_max, min(p.u_max, u));
            u_rec(k) = u;

            % ---- 被控对象更新（连续方程离散化，Euler法）----
            tau_friction = p.Fc*sign(dtheta_sim) + p.Fv*dtheta_sim;
            ddtheta_sim  = (u + tau_disturbance - p.B*dtheta_sim ...
                           - p.K*sin(theta_sim) - tau_friction) / p.J;
            dtheta_sim   = dtheta_sim + ddtheta_sim * dt;
            theta_sim    = theta_sim  + dtheta_sim  * dt;
            % 关节限位
            theta_sim    = max(p.theta_min, min(deg2rad(135), theta_sim));

            theta_rec(k) = theta_sim;
            e_prev2      = e_prev;
            e_prev       = e;
            if ly == 2, u_prev = u; end
        end

        % ---- 计算性能指标 ----
        err = theta_d - theta_rec;
        RMSE(ly,sc)      = sqrt(mean(err.^2));
        PeakError(ly,sc) = max(abs(err));
        Energy(ly,sc)    = sum(u_rec.^2) * dt;

        % 超调量（首个周期内的最大超出量）
        T1_idx = find(t_vec <= p.T_period);
        if ~isempty(T1_idx)
            theta_max_1 = max(theta_rec(T1_idx));
            overshoot = (theta_max_1 - max(theta_d(T1_idx)));
            Overshoot(ly,sc) = max(0, overshoot / max(theta_d) * 100);
        end

        % 调节时间（误差进入±2°带）
        band = deg2rad(2);
        settle_idx = find(abs(err) < band, 1, 'first');
        if ~isempty(settle_idx)
            SettleTime(ly,sc) = t_vec(settle_idx);
        else
            SettleTime(ly,sc) = T_sim;
        end

        % 保存轨迹
        theta_all(ly,sc,:) = theta_rec;
        u_all(ly,sc,:)     = u_rec;

        fprintf(' RMSE=%.4f°, Emax=%.4f°\n', ...
                rad2deg(RMSE(ly,sc)), rad2deg(PeakError(ly,sc)));
    end
end

%% ── 汇总性能对比表 ──────────────────────────────────────────────────
fprintf('\n╔══════════════════════════════════════════════════════════╗\n');
fprintf('║               六层控制器性能对比汇总表                  ║\n');
fprintf('╠══════════════════════════════════════════════════════════╣\n');
fprintf('║ 控制层次         │  RMSE[°]  │  峰值误差[°]  │  能耗  ║\n');
fprintf('╠══════════════════════════════════════════════════════════╣\n');
for ly = 1:n_layer
    fprintf('║ %-16s │  %7.4f  │  %11.4f  │%6.1f  ║\n', ...
            layer_names{ly}, rad2deg(RMSE(ly,1)), ...
            rad2deg(PeakError(ly,1)), Energy(ly,1));
end
fprintf('╚══════════════════════════════════════════════════════════╝\n');

%% ── 专业对比图表（实验一绘图技能的完整综合应用）────────────────────
fig = figure('Name','六层控制器横向对比分析报告', ...
             'Position',[20,20,1600,1000]);

% 配色方案（Matlab推荐配色）
colors = [0.0,0.4,0.8;   % L1 蓝（基准）
          0.9,0.3,0.0;   % L2 橙（专家）
          0.2,0.7,0.2;   % L3 绿（模糊）
          0.6,0.0,0.8;   % L4 紫（RBF）
          0.8,0.6,0.0;   % L5 金（PSO）
          0.0,0.6,0.6];  % L6 青（ILC）

% ── 图1：正常工况下轨迹对比（所有层次）
ax1 = subplot(3,4,1:2);
plot(t_vec, rad2deg(theta_d), 'k--', 'LineWidth', 2.5, ...
     'DisplayName','期望轨迹'); hold on;
for ly = [1,2,3,4]
    plot(t_vec, rad2deg(squeeze(theta_all(ly,1,:))), ...
         'Color', colors(ly,:), 'LineWidth', 1.5, ...
         'DisplayName', layer_names{ly});
end
grid on; xlabel('时间 [s]'); ylabel('关节角度 [°]');
title('正常工况：L1-L4 轨迹跟踪对比');
legend('Location','best','FontSize',7); xlim([0,12]);

ax2 = subplot(3,4,3:4);
plot(t_vec, rad2deg(theta_d), 'k--', 'LineWidth', 2.5, ...
     'DisplayName','期望轨迹'); hold on;
for ly = [4,5,6]
    plot(t_vec, rad2deg(squeeze(theta_all(ly,1,:))), ...
         'Color', colors(ly,:), 'LineWidth', 1.5, ...
         'DisplayName', layer_names{ly});
end
grid on; xlabel('时间 [s]'); ylabel('关节角度 [°]');
title('正常工况：L4-L6 轨迹跟踪对比（高精度层）');
legend('Location','best','FontSize',7); xlim([0,12]);

% ── 图2：三种工况下的RMSE对比柱状图
subplot(3,4,5);
RMSE_deg = rad2deg(RMSE);
b = bar(RMSE_deg, 'grouped');
for ly = 1:n_layer
    b(ly).FaceColor = colors(ly,:);
end
set(gca,'XTickLabel', scenario_names);
legend(layer_names, 'Location','northeast', 'FontSize',7);
ylabel('RMSE [°]'); title('各工况RMSE对比');
grid on;

% ── 图3：峰值误差对比
subplot(3,4,6);
PeakError_deg = rad2deg(PeakError);
b2 = bar(PeakError_deg, 'grouped');
for ly = 1:n_layer; b2(ly).FaceColor = colors(ly,:); end
set(gca,'XTickLabel', scenario_names);
legend(layer_names, 'Location','northeast', 'FontSize',7);
ylabel('最大误差 [°]'); title('峰值误差对比（安全指标）');
grid on;
yline(5, 'r--', '安全阈值5°', 'LineWidth',2);

% ── 图4：控制能耗对比
subplot(3,4,7);
b3 = bar(Energy, 'grouped');
for ly = 1:n_layer; b3(ly).FaceColor = colors(ly,:); end
set(gca,'XTickLabel', scenario_names);
legend(layer_names, 'Location','northeast', 'FontSize',7);
ylabel('控制能耗 ∫u²dt'); title('控制能耗对比（效率指标）');
grid on;

% ── 图5：痉挛工况下各层误差响应（关键抗扰对比）
subplot(3,4,8);
spasm_t = find(t_vec <= 20);
for ly = [1,2,3,6]
    err_sc3 = theta_d - squeeze(theta_all(ly,3,:))';
    plot(t_vec, rad2deg(err_sc3), 'Color', colors(ly,:), ...
         'LineWidth', 1.5, 'DisplayName', layer_names{ly}); hold on;
end
grid on; xlabel('时间 [s]'); ylabel('跟踪误差 [°]');
title('痉挛工况误差响应对比'); legend('Location','best','FontSize',7);
yline(5,'r--'); yline(-5,'r--');

% ── 图6：雷达图（综合性能评估）
subplot(3,4,9:10);
metrics_radar = [RMSE(:,1), PeakError(:,1), Energy(:,1)/max(Energy(:,1))*5, ...
                 Overshoot(:,1), SettleTime(:,1)];
metrics_radar_norm = metrics_radar ./ max(metrics_radar); % 归一化
theta_radar = linspace(0, 2*pi, 6); theta_radar(end) = theta_radar(1);
metric_labels = {'RMSE','峰值误差','能耗','超调','调节时间'};
ax_r = polaraxes;
for ly = [1,2,3,4,5,6]
    data = [metrics_radar_norm(ly,:), metrics_radar_norm(ly,1)];
    polarplot(ax_r, theta_radar, data, 'Color', colors(ly,:), ...
              'LineWidth', 2, 'DisplayName', layer_names{ly});
    hold(ax_r, 'on');
end
ax_r.ThetaTick = (0:4) * 72;
ax_r.ThetaTickLabel = metric_labels;
legend('Location','southoutside', 'NumColumns', 3, 'FontSize', 7);
title('综合性能雷达图（归一化）');

% ── 图7：改善百分比（相对L1的提升）
subplot(3,4,11:12);
improve_pct = (1 - RMSE ./ RMSE(1,:)) * 100;
b4 = bar(improve_pct(2:end,:), 'grouped');
for ly = 1:n_layer-1; b4(ly).FaceColor = colors(ly+1,:); end
set(gca,'XTickLabel', scenario_names);
legend(layer_names(2:end), 'Location','northwest', 'FontSize',7);
ylabel('相对L1-PID的RMSE改善 (%)');
title('各层相对基准PID的改善幅度');
grid on; yline(0, 'k-');

sgtitle('六层递进式智能控制系统——综合性能对比分析报告', ...
        'FontSize', 14, 'FontWeight', 'bold');

%% ── 保存结果 ────────────────────────────────────────────────────────
results.theta_all   = theta_all;
results.u_all       = u_all;
results.RMSE        = RMSE;
results.PeakError   = PeakError;
results.Overshoot   = Overshoot;
results.Energy      = Energy;
results.SettleTime  = SettleTime;
results.layer_names = layer_names;
results.scenarios   = scenario_names;
save('comparison_results.mat', 'results');

fprintf('\n[Done] 对比分析完成！结果保存至 comparison_results.mat\n');
fprintf('图表可直接导出用于课程报告（File→Export Setup→300dpi PNG）\n');

%% ── 辅助函数 ────────────────────────────────────────────────────────
function [u, u_prev, I_term, e_prev2] = expert_pid_step(...
        e, de, u_prev, I_term, e_prev2, e_prev, ctrl_e, dt)
% 专家PID单步计算（对应expert_pid_sfunc.m的输出函数简化版）
    M1 = ctrl_e.M1; M2 = ctrl_e.M2; eps = ctrl_e.eps;
    Kp = ctrl_e.Kp; Ki = ctrl_e.Ki; Kd = ctrl_e.Kd;
    k1 = ctrl_e.k1; k2 = ctrl_e.k2; umax = ctrl_e.umax;

    delta_e      = e - e_prev;
    delta_e_prev = e_prev - e_prev2;

    % ★ R5最高优先级（实验四核心改进点）
    if abs(e) <= eps
        I_term = I_term + Ki * e * dt;
        u = Kp*e + I_term + Kd*delta_e/dt;
    elseif abs(e) > M1
        u = umax * sign(e);
    elseif (e * delta_e > 0) && (abs(e) > M2)
        u = u_prev + k1*(Kp*delta_e + Ki*e*dt + Kd*(delta_e-delta_e_prev));
    elseif (e * delta_e > 0) && (abs(e) <= M2)
        u = u_prev + Kp*delta_e + Ki*e*dt + Kd*(delta_e-delta_e_prev);
    elseif (e * delta_e < 0) && (delta_e*delta_e_prev > 0 || e==0)
        u = u_prev;
    elseif (e * delta_e < 0) && (delta_e*delta_e_prev < 0)
        if abs(e) >= M2; u = u_prev + k1*Kp*e;
        else;            u = u_prev + k2*Kp*e; end
    else
        u = u_prev;
    end

    % 力矩变化率限幅
    du_max = 5.0 * dt;
    u = u_prev + max(-du_max, min(du_max, u - u_prev));
    u = max(-umax, min(umax, u));
    e_prev2 = e_prev;
end

function [theta, dtheta, ddtheta] = min_jerk_traj(t, T, th_min, th_max)
    T_half=T/2; delta=th_max-th_min; t_mod=mod(t,T);
    if t_mod<=T_half; tau=t_mod/T_half; th0=th_min; dth=delta;
    else; tau=(t_mod-T_half)/T_half; th0=th_max; dth=-delta; end
    f=10*tau^3-15*tau^4+6*tau^5;
    df=(30*tau^2-60*tau^3+30*tau^4)/T_half;
    ddf=(60*tau-180*tau^2+120*tau^3)/T_half^2;
    theta=th0+dth*f; dtheta=dth*df; ddtheta=dth*ddf;
end