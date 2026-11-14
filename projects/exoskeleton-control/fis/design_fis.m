%% ========================================================================
%  design_fis.m  ——  模糊PID控制器 FIS 文件设计脚本
%  教材对应：第3章（模糊控制理论基础）+ 第4章（模糊控制器设计）
%  实验对应：实验六（模糊控制理论基础）+ 实验六附录（洗衣机模糊控制系统）
%
%  ■ 设计说明：
%    本脚本以实验六中洗衣机模糊控制器设计流程为模板（直接迁移）
%    将两个输入（污泥、油脂）→ 一个输出（洗涤时间）的结构
%    升级为：两个输入（误差e、误差率ė）→ 三个输出（ΔKp、ΔKi、ΔKd）
%
%  ■ FIS类型：Mamdani推理机（教材第4章4.1节）
%  ■ 去模糊化：重心法（centroid，教材第4章4.1.4节）
% ========================================================================
clear all; close all;
load('exo_workspace.mat', 'ctrl');

fprintf('=== 模糊PID控制器 FIS 文件设计 ===\n');
fprintf('对应教材：第3章（理论基础）+ 第4章（控制器设计）\n\n');

%% ── 1. 创建Mamdani型FIS ─────────────────────────────────────────────
% 教材第4章4.1节：模糊控制器的组成 = 模糊化 + 规则库 + 推理机 + 去模糊化
fis = mamfis('Name', 'KneeFuzzyPID');

%% ── 2. 定义输入变量 ──────────────────────────────────────────────────
% 输入1：误差 e（关节角度误差，单位：rad）
% 论域 [-π/2, π/2] 对应 [-90°, 90°]
% 教材第3章3.3节：隶属函数设计（三角形+梯形组合）
fis = addInput(fis, [-pi/2, pi/2], 'Name', 'e');

% 误差的7个模糊等级（教材实验六中七等级三角形隶属函数的直接迁移）
% NB=负大, NM=负中, NS=负小, ZE=零, PS=正小, PM=正中, PB=正大
e_centers = linspace(-pi/2, pi/2, 7); % [-90,-60,-30,0,30,60,90]°
e_width   = pi/6;                      % 等间距宽度（30°）

mf_names_e = {'NB','NM','NS','ZE','PS','PM','PB'};
for i = 1:7
    if i == 1
        % 边界处用梯形（教材3.3节：边界隶属函数用梯形保证全覆盖）
        params = [e_centers(i)-e_width, e_centers(i)-e_width, ...
                  e_centers(i), e_centers(i)+e_width];
        fis = addMF(fis, 'e', 'trapmf', params, 'Name', mf_names_e{i});
    elseif i == 7
        params = [e_centers(i)-e_width, e_centers(i), ...
                  e_centers(i)+e_width, e_centers(i)+e_width];
        fis = addMF(fis, 'e', 'trapmf', params, 'Name', mf_names_e{i});
    else
        % 内部用三角形（实验六设计经验：三角形规整且计算高效）
        params = [e_centers(i)-e_width, e_centers(i), e_centers(i)+e_width];
        fis = addMF(fis, 'e', 'trimf', params, 'Name', mf_names_e{i});
    end
end

% 输入2：误差变化率 ė（角速度误差，单位：rad/s）
% 论域 [-π/4, π/4] 对应 [-45°/s, 45°/s]（康复运动速度范围）
fis = addInput(fis, [-pi/4, pi/4], 'Name', 'de');
de_centers = linspace(-pi/4, pi/4, 7);
de_width   = pi/12;

mf_names_de = {'NB','NM','NS','ZE','PS','PM','PB'};
for i = 1:7
    if i == 1
        params = [de_centers(i)-de_width, de_centers(i)-de_width, ...
                  de_centers(i), de_centers(i)+de_width];
        fis = addMF(fis, 'de', 'trapmf', params, 'Name', mf_names_de{i});
    elseif i == 7
        params = [de_centers(i)-de_width, de_centers(i), ...
                  de_centers(i)+de_width, de_centers(i)+de_width];
        fis = addMF(fis, 'de', 'trapmf', params, 'Name', mf_names_de{i});
    else
        params = [de_centers(i)-de_width, de_centers(i), de_centers(i)+de_width];
        fis = addMF(fis, 'de', 'trimf', params, 'Name', mf_names_de{i});
    end
end

fprintf('[Step 1] 输入变量定义完毕（e: 7级, ė: 7级 → 49条规则）\n');

%% ── 3. 定义输出变量 ──────────────────────────────────────────────────
% 输出1：ΔKp增量（比例系数调整量）
fis = addOutput(fis, [-10, 10], 'Name', 'dKp');
% 输出2：ΔKi增量（积分系数调整量）
fis = addOutput(fis, [-0.5, 0.5], 'Name', 'dKi');
% 输出3：ΔKd增量（微分系数调整量）
fis = addOutput(fis, [-1, 1], 'Name', 'dKd');

% 为每个输出定义隶属函数（5个三角形等级：NB/NS/ZE/PS/PB）
output_names  = {'dKp','dKi','dKd'};
output_ranges = {[-10,10], [-0.5,0.5], [-1,1]};

for oi = 1:3
    rng = output_ranges{oi};
    centers_out = linspace(rng(1), rng(2), 5);
    width_out   = (rng(2)-rng(1)) / 4;
    out_mf_names = {'NB','NS','ZE','PS','PB'};
    for j = 1:5
        if j == 1
            params = [centers_out(j)-width_out, centers_out(j)-width_out, ...
                      centers_out(j), centers_out(j)+width_out];
            fis = addMF(fis, output_names{oi}, 'trapmf', params, ...
                        'Name', out_mf_names{j});
        elseif j == 5
            params = [centers_out(j)-width_out, centers_out(j), ...
                      centers_out(j)+width_out, centers_out(j)+width_out];
            fis = addMF(fis, output_names{oi}, 'trapmf', params, ...
                        'Name', out_mf_names{j});
        else
            params = [centers_out(j)-width_out, centers_out(j), ...
                      centers_out(j)+width_out];
            fis = addMF(fis, output_names{oi}, 'trimf', params, ...
                        'Name', out_mf_names{j});
        end
    end
end

fprintf('[Step 2] 输出变量定义完毕（dKp/dKi/dKd 各5个模糊等级）\n');

%% ── 4. 建立49条模糊规则表 ────────────────────────────────────────────
% 规则设计准则（教材第4章4.3节 控制器设计原则）：
%   (a) 误差|e|大时：增大Kp（快速响应），减小Kd（避免微分饱和）
%   (b) |e|小时：减小Kp，增大Ki（消除稳态误差）
%   (c) ė与e同向（误差增大）时：增大Kd（预测性抑制）
%   (d) 误差趋零时：减小Kp，增大Ki
%
% 规则格式：[e_idx, de_idx, dKp_idx, dKi_idx, dKd_idx, weight, conn]
% 模糊等级索引：1=NB,2=NM,3=NS,4=ZE,5=PS,6=PM,7=PB（输入7级）
%               1=NB,2=NS,3=ZE,4=PS,5=PB（输出5级）

% ΔKp 规则表（7×7）：行=e的等级，列=ė的等级
% 规则：误差越大→Kp越大；误差接近零→Kp越小
dKp_table = [
%  de: NB  NM  NS  ZE  PS  PM  PB     % e:
    5   5   4   4   4   5   5;         % NB（e负大→需要大Kp快速纠偏）
    5   4   4   3   4   4   5;         % NM
    4   4   3   3   3   4   4;         % NS
    3   3   3   3   3   3   3;         % ZE（误差为零→Kp中等）
    4   4   3   3   3   4   4;         % PS
    5   4   4   3   4   4   5;         % PM
    5   5   4   4   4   5   5;         % PB（e正大→需要大Kp）
];

% ΔKi 规则表（7×7）：误差小且稳定时增大Ki消除稳态误差
dKi_table = [
%  de: NB  NM  NS  ZE  PS  PM  PB     % e:
    1   1   1   1   1   1   1;         % NB（大误差→不积分，避免积分饱和）
    1   1   2   2   2   1   1;         % NM
    2   2   3   3   3   2   2;         % NS
    3   4   4   5   4   4   3;         % ZE（误差为零→最大Ki精细消差）
    2   2   3   3   3   2   2;         % PS
    1   1   2   2   2   1   1;         % PM
    1   1   1   1   1   1   1;         % PB
];

% ΔKd 规则表（7×7）：误差变化快时增大Kd预测并抑制
dKd_table = [
%  de: NB  NM  NS  ZE  PS  PM  PB     % e:
    5   4   3   3   3   4   5;         % NB（误差变化快→大Kd抑制超调）
    4   4   3   2   3   4   4;         % NM
    3   3   3   2   3   3   3;         % NS
    2   2   2   2   2   2   2;         % ZE
    3   3   3   2   3   3   3;         % PS
    4   4   3   2   3   4   4;         % PM
    5   4   3   3   3   4   5;         % PB
];

% 将规则表转换为FIS规则格式并添加
rule_count = 0;
for ei = 1:7
    for dei = 1:7
        dKp_idx = dKp_table(ei, dei);
        dKi_idx = dKi_table(ei, dei);
        dKd_idx = dKd_table(ei, dei);

        % 规则格式：[输入1索引, 输入2索引, 输出1索引, 输出2索引, 输出3索引, 权重, 连接(1=AND)]
        rule = [ei, dei, dKp_idx, dKi_idx, dKd_idx, 1, 1];
        fis = addRule(fis, rule);
        rule_count = rule_count + 1;
    end
end

fprintf('[Step 3] 模糊规则库建立完毕（共 %d 条规则）\n', rule_count);

%% ── 5. 设置去模糊化方法 ─────────────────────────────────────────────
% 教材第4章4.1.4节：重心法（centroid）是最常用的去模糊化方法
% 对应实验六：evalfis函数内部使用centroid方法
fis.DefuzzificationMethod = 'centroid';
fis.AndMethod = 'min';           % Mamdani模型使用min操作
fis.OrMethod  = 'max';           % 并操作
fis.ImplicationMethod = 'min';   % 蕴含：min（Mamdani标准）
fis.AggregationMethod = 'max';   % 聚合：max

%% ── 6. 验证FIS并可视化 ──────────────────────────────────────────────
fprintf('[Step 4] FIS验证：在e=0.05rad, ė=0.02rad/s处测试推理...\n');
test_in = [0.05, 0.02];
test_out = evalfis(fis, test_in);
fprintf('  输入[e=0.05rad, ė=0.02rad/s] → [ΔKp=%.3f, ΔKi=%.4f, ΔKd=%.4f]\n', ...
        test_out(1), test_out(2), test_out(3));

% 绘制隶属函数曲线（实验六图形绘制技能的直接应用）
figure('Name','模糊PID控制器 隶属函数可视化', 'Position',[100,100,1200,800]);
subplot(3,3,1);
plotmf(fis,'input',1); title('输入1: 误差 e'); xlabel('e [rad]');
subplot(3,3,2);
plotmf(fis,'input',2); title('输入2: 误差率 ė'); xlabel('ė [rad/s]');
subplot(3,3,4);
plotmf(fis,'output',1); title('输出1: ΔKp'); xlabel('ΔKp');
subplot(3,3,5);
plotmf(fis,'output',2); title('输出2: ΔKi'); xlabel('ΔKi');
subplot(3,3,6);
plotmf(fis,'output',3); title('输出3: ΔKd'); xlabel('ΔKd');

% 绘制控制曲面（ΔKp 关于 e 和 ė 的输出曲面）
subplot(3,3,7);
gensurf(fis,[1 2],1); title('ΔKp 输出曲面'); colorbar;
subplot(3,3,8);
gensurf(fis,[1 2],2); title('ΔKi 输出曲面'); colorbar;
subplot(3,3,9);
gensurf(fis,[1 2],3); title('ΔKd 输出曲面'); colorbar;

%% ── 7. 保存FIS文件 ───────────────────────────────────────────────────
writeFIS(fis, 'knee_fuzzy_pid');
fprintf('[Done] FIS文件已保存: knee_fuzzy_pid.fis\n');
fprintf('下一步：在Simulink中将 Fuzzy Logic Controller 模块的FIS参数设置为此文件\n');

%% ── 8. 测试完整模糊PID响应曲线 ──────────────────────────────────────
fprintf('\n[Test] 模拟模糊PID在阶跃误差下的参数调整过程...\n');
e_range = linspace(-pi/2, pi/2, 100);
Kp_base = ctrl.fuzzy.Kp_base;
Ki_base = ctrl.fuzzy.Ki_base;
Kd_base = ctrl.fuzzy.Kd_base;

Kp_out = zeros(100,1);
Ki_out = zeros(100,1);
Kd_out = zeros(100,1);

for i = 1:100
    out = evalfis(fis, [e_range(i), 0]);  % ė=0
    Kp_out(i) = max(0.1, Kp_base + out(1));
    Ki_out(i) = max(0.0, Ki_base + out(2));
    Kd_out(i) = max(0.0, Kd_base + out(3));
end

figure('Name','模糊PID 参数自适应曲线', 'Position',[100,100,900,400]);
e_deg = rad2deg(e_range);
subplot(1,3,1); plot(e_deg, Kp_out,'b-','LineWidth',2);
grid on; xlabel('误差 e [°]'); ylabel('Kp'); title('Kp自适应（ė=0）');
subplot(1,3,2); plot(e_deg, Ki_out,'r-','LineWidth',2);
grid on; xlabel('误差 e [°]'); ylabel('Ki'); title('Ki自适应（ė=0）');
subplot(1,3,3); plot(e_deg, Kd_out,'g-','LineWidth',2);
grid on; xlabel('误差 e [°]'); ylabel('Kd'); title('Kd自适应（ė=0）');
sgtitle('模糊PID参数随误差的自适应变化曲线（教材第4章图示）');