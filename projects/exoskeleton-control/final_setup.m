%% ========================================================================
%  final_setup.m  -  下肢外骨骼控制系统完整配置脚本
%  文件夹已重命名：期末项目 → 1
%  此脚本完成所有初始化、路径配置、模块修复和验证
% ========================================================================
clear all; close all; clc;

fprintf('╔════════════════════════════════════════════════════════╗\n');
fprintf('║    下肢外骨骼康复机器人多层次混合智能控制系统          ║\n');
fprintf('║              完整配置与验证脚本                        ║\n');
fprintf('╚════════════════════════════════════════════════════════╝\n\n');

%% ========================================================================
%  第一步：路径配置与参数加载
% ========================================================================
fprintf('【步骤 1/10】 路径配置与参数加载\n');
fprintf('─────────────────────────────────────────────────────────\n');

% 新的项目路径
PROJECT_ROOT = 'E:\college\ICT\1\exo_project';

% 检查路径是否存在
if ~exist(PROJECT_ROOT, 'dir')
    error('✗ 项目路径不存在！请确认文件夹已重命名为 "1"');
end

% 切换到项目目录
cd(PROJECT_ROOT);
fprintf('当前工作目录: %s\n', pwd);

% 添加所有子目录到路径
addpath(genpath(PROJECT_ROOT));
fprintf('✓ 路径已添加\n');

% 加载参数文件
if exist('exo_workspace.mat', 'file')
    load('exo_workspace.mat', 'p', 'ctrl');
    fprintf('✓ 参数文件已加载\n');
else
    error('✗ exo_workspace.mat 不存在，请先运行 init_plant.m');
end

% 验证参数
fprintf('  关键参数验证:\n');
fprintf('    p.dt = %.4f s\n', p.dt);
fprintf('    p.u_max = %.2f N·m\n', p.u_max);
fprintf('    ctrl.fuzzy.Kp_base = %.2f\n', ctrl.fuzzy.Kp_base);

fprintf('\n');

%% ========================================================================
%  第二步：验证和准备FIS文件
% ========================================================================
fprintf('【步骤 2/10】 模糊控制器FIS文件准备\n');
fprintf('─────────────────────────────────────────────────────────\n');

% 检查FIS文件
fis_path_original = fullfile(PROJECT_ROOT, 'fis', 'knee_fuzzy_pid.fis');
fis_path_root = fullfile(PROJECT_ROOT, 'knee_fuzzy_pid.fis');

if exist(fis_path_original, 'file')
    fprintf('✓ FIS文件存在于 fis/ 目录\n');
    
    % 复制到根目录（便于MATLAB Function访问）
    copyfile(fis_path_original, fis_path_root);
    fprintf('✓ FIS文件已复制到项目根目录\n');
else
    fprintf('✗ FIS文件不存在，正在生成...\n');
    cd('fis');
    run('design_fis.m');
    cd(PROJECT_ROOT);
    copyfile(fis_path_original, fis_path_root);
    fprintf('✓ FIS文件已生成并复制\n');
end

% 验证FIS
try
    fis_test = readfis('knee_fuzzy_pid.fis');
    fprintf('✓ FIS文件验证成功\n');
    fprintf('  输入数量: %d\n', length(fis_test.Inputs));
    fprintf('  输出数量: %d\n', length(fis_test.Outputs));
    
    % 测试推理
    test_output = evalfis(fis_test, [0.1, 0.05]);
    fprintf('  测试推理: e=0.1, de=0.05 → [ΔKp=%.3f, ΔKi=%.4f, ΔKd=%.4f]\n', ...
            test_output(1), test_output(2), test_output(3));
catch ME
    error('✗ FIS文件验证失败: %s', ME.message);
end

fprintf('\n');

%% ========================================================================
%  第三步：打开并配置Simulink模型
% ========================================================================
fprintf('【步骤 3/10】 打开Simulink模型\n');
fprintf('─────────────────────────────────────────────────────────\n');

model_name = 'exo_rehab_system';
model_path = fullfile(PROJECT_ROOT, [model_name '.slx']);

if ~exist(model_path, 'file')
    error('✗ Simulink模型文件不存在: %s', model_path);
end

% 如果模型已打开，先关闭
if bdIsLoaded(model_name)
    close_system(model_name, 0);
    fprintf('○ 已关闭旧模型实例\n');
end

% 打开模型
open_system(model_path);
fprintf('✓ 模型已打开: %s\n', model_name);

fprintf('\n');

%% ========================================================================
%  第四步：配置模型回调函数（自动加载参数）
% ========================================================================
fprintf('【步骤 4/10】 配置模型回调函数\n');
fprintf('─────────────────────────────────────────────────────────\n');

% PreLoadFcn - 模型加载前执行
preload_code = sprintf('cd(''%s''); addpath(genpath(pwd));', PROJECT_ROOT);
set_param(model_name, 'PreLoadFcn', preload_code);
fprintf('✓ PreLoadFcn 已设置\n');

% InitFcn - 模型初始化时执行
init_code = sprintf(['cd(''%s''); ', ...
                     'addpath(genpath(pwd)); ', ...
                     'load(''exo_workspace.mat'', ''p'', ''ctrl'');'], ...
                     PROJECT_ROOT);
set_param(model_name, 'InitFcn', init_code);
fprintf('✓ InitFcn 已设置\n');

% 保存模型
save_system(model_name);
fprintf('✓ 模型已保存\n');

fprintf('\n');

%% ========================================================================
%  第五步：修复Fuzzy_Logic_Evaluator模块（无中文版本）
% ========================================================================
fprintf('【步骤 5/10】 修复Fuzzy_Logic_Evaluator模块\n');
fprintf('─────────────────────────────────────────────────────────\n');

fuzzy_eval_block = [model_name '/Fuzzy_Logic_Evaluator'];

% 检查模块是否存在
if isempty(find_system(model_name, 'Name', 'Fuzzy_Logic_Evaluator'))
    fprintf('○ 模块不存在，正在创建...\n');
    add_block('simulink/User-Defined Functions/MATLAB Function', fuzzy_eval_block);
    set_param(fuzzy_eval_block, 'Position', [300, 200, 400, 280]);
end

% MATLAB Function代码（纯英文，无中文）
fuzzy_code = [...
'function [delta_Kp, delta_Ki, delta_Kd] = fcn(e, de)', newline, ...
'%#codegen', newline, ...
'% Fuzzy Logic Evaluator - No Chinese characters', newline, ...
'', newline, ...
'persistent fis', newline, ...
'', newline, ...
'if isempty(fis)', newline, ...
'    fis_file = ''knee_fuzzy_pid.fis'';', newline, ...
'    ', newline, ...
'    if exist(fis_file, ''file'')', newline, ...
'        fis = readfis(fis_file);', newline, ...
'    else', newline, ...
'        delta_Kp = 0;', newline, ...
'        delta_Ki = 0;', newline, ...
'        delta_Kd = 0;', newline, ...
'        return;', newline, ...
'    end', newline, ...
'end', newline, ...
'', newline, ...
'output = evalfis(fis, [e, de]);', newline, ...
'', newline, ...
'delta_Kp = output(1);', newline, ...
'delta_Ki = output(2);', newline, ...
'delta_Kd = output(3);', newline, ...
'', newline, ...
'end', newline];

% 使用Stateflow API设置代码
try
    sf_chart = find(sfroot, '-isa', 'Stateflow.EMChart', ...
                    'Path', fuzzy_eval_block);
    if ~isempty(sf_chart)
        sf_chart.Script = fuzzy_code;
        fprintf('✓ Fuzzy_Logic_Evaluator 代码已更新\n');
    else
        fprintf('⚠ 无法自动更新代码，请手动更新\n');
        fprintf('请双击 Fuzzy_Logic_Evaluator 模块，粘贴以下代码：\n');
        fprintf('────────────────────────────────────────\n');
        fprintf('%s', fuzzy_code);
        fprintf('────────────────────────────────────────\n');
        fprintf('完成后按Enter继续...\n');
        pause;
    end
catch
    fprintf('⚠ 自动更新失败，请手动操作\n');
    fprintf('请双击 Fuzzy_Logic_Evaluator 模块，删除所有代码并粘贴：\n');
    fprintf('────────────────────────────────────────\n');
    fprintf('%s', fuzzy_code);
    fprintf('────────────────────────────────────────\n');
    fprintf('完成后按Enter继续...\n');
    pause;
end

fprintf('\n');

%% ========================================================================
%  第六步：修复Fuzzy_PID_Calculator模块（无中文版本）
% ========================================================================
fprintf('【步骤 6/10】 修复Fuzzy_PID_Calculator模块\n');
fprintf('─────────────────────────────────────────────────────────\n');

fuzzy_pid_block = [model_name '/Fuzzy_PID_Calculator'];

% 检查模块是否存在
if isempty(find_system(model_name, 'Name', 'Fuzzy_PID_Calculator'))
    fprintf('○ 模块不存在，正在创建...\n');
    add_block('simulink/User-Defined Functions/MATLAB Function', fuzzy_pid_block);
    set_param(fuzzy_pid_block, 'Position', [500, 300, 600, 400]);
end

% MATLAB Function代码（11输入2输出，纯英文）
fuzzy_pid_code = [...
'function [u, e_int] = fcn(e, de, delta_Kp, delta_Ki, delta_Kd, e_int_prev, Kp_base, Ki_base, Kd_base, ts, u_max)', newline, ...
'%#codegen', newline, ...
'% Fuzzy PID Calculator - No Chinese characters', newline, ...
'', newline, ...
'% Compute adaptive PID parameters', newline, ...
'Kp = max(0.1, Kp_base + delta_Kp);', newline, ...
'Ki = max(0.0, Ki_base + delta_Ki);', newline, ...
'Kd = max(0.0, Kd_base + delta_Kd);', newline, ...
'', newline, ...
'% Compute error integral', newline, ...
'e_int = e_int_prev + e * ts;', newline, ...
'', newline, ...
'% Anti-windup', newline, ...
'I_max = u_max / max(Ki, 0.01);', newline, ...
'e_int = max(-I_max, min(I_max, e_int));', newline, ...
'', newline, ...
'% PID control law', newline, ...
'u = Kp * e + Ki * e_int + Kd * de;', newline, ...
'', newline, ...
'% Output saturation', newline, ...
'u = max(-u_max, min(u_max, u));', newline, ...
'', newline, ...
'end', newline];

% 设置代码
try
    sf_chart = find(sfroot, '-isa', 'Stateflow.EMChart', ...
                    'Path', fuzzy_pid_block);
    if ~isempty(sf_chart)
        sf_chart.Script = fuzzy_pid_code;
        fprintf('✓ Fuzzy_PID_Calculator 代码已更新\n');
    else
        fprintf('⚠ 请手动更新 Fuzzy_PID_Calculator 代码\n');
        fprintf('────────────────────────────────────────\n');
        fprintf('%s', fuzzy_pid_code);
        fprintf('────────────────────────────────────────\n');
        fprintf('完成后按Enter继续...\n');
        pause;
    end
catch
    fprintf('⚠ 请手动更新 Fuzzy_PID_Calculator 代码\n');
    fprintf('────────────────────────────────────────\n');
    fprintf('%s', fuzzy_pid_code);
    fprintf('────────────────────────────────────────\n');
    fprintf('完成后按Enter继续...\n');
    pause;
end

fprintf('\n');

%% ========================================================================
%  第七步：创建5个Constant模块
% ========================================================================
fprintf('【步骤 7/10】 创建参数Constant模块\n');
fprintf('─────────────────────────────────────────────────────────\n');

% 定义5个Constant
constants_config = {
    'Param_Kp_base', ctrl.fuzzy.Kp_base, [350, 300, 430, 320];
    'Param_Ki_base', ctrl.fuzzy.Ki_base, [350, 330, 430, 350];
    'Param_Kd_base', ctrl.fuzzy.Kd_base, [350, 360, 430, 380];
    'Param_ts',      p.dt,               [350, 390, 430, 410];
    'Param_umax',    p.u_max,            [350, 420, 430, 440]
};

for i = 1:size(constants_config, 1)
    block_path = [model_name '/' constants_config{i,1}];
    
    % 检查是否已存在
    if isempty(find_system(model_name, 'SearchDepth', 1, ...
                           'Name', constants_config{i,1}))
        % 创建Constant
        add_block('simulink/Sources/Constant', block_path);
        
        % 设置值
        set_param(block_path, 'Value', num2str(constants_config{i,2}));
        
        % 设置位置
        set_param(block_path, 'Position', constants_config{i,3});
        
        fprintf('  ✓ 创建: %s = %.6f\n', constants_config{i,1}, constants_config{i,2});
    else
        fprintf('  ○ 已存在: %s\n', constants_config{i,1});
    end
end

fprintf('✓ 所有Constant模块已准备\n');

fprintf('\n');

%% ========================================================================
%  第八步：创建Memory模块
% ========================================================================
fprintf('【步骤 8/10】 创建Memory_Integral模块\n');
fprintf('─────────────────────────────────────────────────────────\n');

mem_block = [model_name '/Memory_Integral'];

if isempty(find_system(model_name, 'SearchDepth', 1, 'Name', 'Memory_Integral'))
    add_block('simulink/Discrete/Memory', mem_block);
    set_param(mem_block, 'InitialCondition', '0');
    set_param(mem_block, 'Position', [650, 350, 680, 370]);
    fprintf('✓ Memory_Integral 模块已创建\n');
else
    fprintf('○ Memory_Integral 模块已存在\n');
end

fprintf('\n');

%% ========================================================================
%  第九步：保存模型并编译测试
% ========================================================================
fprintf('【步骤 9/10】 编译测试\n');
fprintf('─────────────────────────────────────────────────────────\n');

save_system(model_name);
fprintf('✓ 模型已保存\n');

fprintf('\n正在编译模型...\n');

try
    % 编译模型
    eval([model_name '([],[],[],''compile'')']);
    fprintf('✓✓✓ 模型编译成功！✓✓✓\n');
    
    % 终止编译
    eval([model_name '([],[],[],''term'')']);
    
    compilation_success = true;
catch ME
    fprintf('✗ 编译失败：%s\n', ME.message);
    fprintf('\n错误详情：\n');
    for i = 1:min(3, length(ME.stack))
        fprintf('  文件: %s\n', ME.stack(i).file);
        fprintf('  行号: %d\n', ME.stack(i).line);
    end
    compilation_success = false;
end

fprintf('\n');

%% ========================================================================
%  第十步：生成完整报告
% ========================================================================
fprintf('【步骤 10/10】 生成配置报告\n');
fprintf('─────────────────────────────────────────────────────────\n');

% 创建报告文件
report_file = fullfile(PROJECT_ROOT, 'setup_report.txt');
fid = fopen(report_file, 'w');

fprintf(fid, '═══════════════════════════════════════════════════════\n');
fprintf(fid, '  下肢外骨骼控制系统配置报告\n');
fprintf(fid, '  生成时间: %s\n', datestr(now));
fprintf(fid, '═══════════════════════════════════════════════════════\n\n');

fprintf(fid, '【项目信息】\n');
fprintf(fid, '  项目路径: %s\n', PROJECT_ROOT);
fprintf(fid, '  模型文件: %s.slx\n', model_name);
fprintf(fid, '\n');

fprintf(fid, '【参数加载】\n');
fprintf(fid, '  p.dt = %.4f s\n', p.dt);
fprintf(fid, '  p.u_max = %.2f N·m\n', p.u_max);
fprintf(fid, '  p.T_period = %.2f s\n', p.T_period);
fprintf(fid, '  ctrl.fuzzy.Kp_base = %.2f\n', ctrl.fuzzy.Kp_base);
fprintf(fid, '  ctrl.fuzzy.Ki_base = %.2f\n', ctrl.fuzzy.Ki_base);
fprintf(fid, '  ctrl.fuzzy.Kd_base = %.2f\n', ctrl.fuzzy.Kd_base);
fprintf(fid, '\n');

fprintf(fid, '【FIS文件】\n');
fprintf(fid, '  文件路径: %s\n', fis_path_root);
fprintf(fid, '  输入数量: %d\n', length(fis_test.Inputs));
fprintf(fid, '  输出数量: %d\n', length(fis_test.Outputs));
fprintf(fid, '  规则数量: %d\n', length(fis_test.Rules));
fprintf(fid, '\n');

fprintf(fid, '【模块状态】\n');

% 检查关键模块
key_blocks = {
    'Fuzzy_Logic_Evaluator';
    'Fuzzy_PID_Calculator';
    'Memory_Integral';
    'Param_Kp_base';
    'Param_Ki_base';
    'Param_Kd_base';
    'Param_ts';
    'Param_umax'
};

for i = 1:length(key_blocks)
    blocks_found = find_system(model_name, 'SearchDepth', 1, ...
                                'Name', key_blocks{i});
    if ~isempty(blocks_found)
        fprintf(fid, '  ✓ %s\n', key_blocks{i});
    else
        fprintf(fid, '  ✗ %s (缺失)\n', key_blocks{i});
    end
end

fprintf(fid, '\n');

fprintf(fid, '【编译结果】\n');
if compilation_success
    fprintf(fid, '  ✓✓✓ 编译成功\n');
else
    fprintf(fid, '  ✗ 编译失败\n');
    fprintf(fid, '  错误信息: %s\n', ME.message);
end

fprintf(fid, '\n');

fprintf(fid, '【后续步骤】\n');
if compilation_success
    fprintf(fid, '  1. 手动连接所有信号线（参考连接指南）\n');
    fprintf(fid, '  2. 运行仿真测试\n');
    fprintf(fid, '  3. 执行 compare_results.m 进行性能对比\n');
    fprintf(fid, '  4. 执行 ilc_analysis.m 进行ILC分析\n');
else
    fprintf(fid, '  1. 检查错误信息\n');
    fprintf(fid, '  2. 确认所有MATLAB Function代码无中文\n');
    fprintf(fid, '  3. 重新执行 final_setup.m\n');
end

fprintf(fid, '\n');
fprintf(fid, '═══════════════════════════════════════════════════════\n');

fclose(fid);

fprintf('✓ 配置报告已生成: %s\n', report_file);

fprintf('\n');

%% ========================================================================
%  总结与下一步指引
% ========================================================================
fprintf('╔════════════════════════════════════════════════════════╗\n');
fprintf('║                    配置完成总结                        ║\n');
fprintf('╚════════════════════════════════════════════════════════╝\n\n');

if compilation_success
    fprintf('✅ 状态：编译成功\n\n');
    
    fprintf('📋 下一步操作：\n');
    fprintf('─────────────────────────────────────────────────────────\n');
    fprintf('1. 手动连接信号线（11个输入 + 2个输出）\n');
    fprintf('   参考之前的连接指南完成所有连接\n\n');
    
    fprintf('2. 运行仿真测试：\n');
    fprintf('   >> sim(''%s'')\n\n', model_name);
    
    fprintf('3. 性能对比分析：\n');
    fprintf('   >> cd analysis\n');
    fprintf('   >> compare_results\n\n');
    
    fprintf('4. ILC学习分析：\n');
    fprintf('   >> ilc_analysis\n\n');
    
else
    fprintf('⚠️ 状态：编译失败\n\n');
    
    fprintf('🔧 故障排查：\n');
    fprintf('─────────────────────────────────────────────────────────\n');
    fprintf('1. 检查MATLAB Function代码中是否仍有中文字符\n');
    fprintf('2. 确认FIS文件路径正确\n');
    fprintf('3. 查看详细错误信息：\n');
    fprintf('   >> open_system(''%s'')\n', model_name);
    fprintf('   >> 点击菜单 Simulation → Model Configuration Parameters\n');
    fprintf('   >> 检查Diagnostics设置\n\n');
end

fprintf('📁 项目文件位置：\n');
fprintf('   %s\n\n', PROJECT_ROOT);

fprintf('📊 配置报告：\n');
fprintf('   %s\n\n', report_file);

fprintf('═══════════════════════════════════════════════════════════\n');

%% ========================================================================
%  可选：自动打开帮助文档
% ========================================================================
fprintf('\n是否打开连接指南文档？(y/n): ');
user_input = input('', 's');

if strcmpi(user_input, 'y')
    % 创建连接指南
    guide_file = fullfile(PROJECT_ROOT, 'CONNECTION_GUIDE.txt');
    fid_guide = fopen(guide_file, 'w');
    
    fprintf(fid_guide, '═══════════════════════════════════════════════════════\n');
    fprintf(fid_guide, '  模糊PID控制器信号连接指南\n');
    fprintf(fid_guide, '═══════════════════════════════════════════════════════\n\n');
    
    fprintf(fid_guide, 'Fuzzy_PID_Calculator 输入连接：\n');
    fprintf(fid_guide, '  输入1:  e           ← Error_Calculation\n');
    fprintf(fid_guide, '  输入2:  de          ← Error_Derivative\n');
    fprintf(fid_guide, '  输入3:  delta_Kp    ← Demux输出1 (或Fuzzy输出1)\n');
    fprintf(fid_guide, '  输入4:  delta_Ki    ← Demux输出2 (或Fuzzy输出2)\n');
    fprintf(fid_guide, '  输入5:  delta_Kd    ← Demux输出3 (或Fuzzy输出3)\n');
    fprintf(fid_guide, '  输入6:  e_int_prev  ← Memory_Integral\n');
    fprintf(fid_guide, '  输入7:  Kp_base     ← Param_Kp_base\n');
    fprintf(fid_guide, '  输入8:  Ki_base     ← Param_Ki_base\n');
    fprintf(fid_guide, '  输入9:  Kd_base     ← Param_Kd_base\n');
    fprintf(fid_guide, '  输入10: ts          ← Param_ts\n');
    fprintf(fid_guide, '  输入11: u_max       ← Param_umax\n\n');
    
    fprintf(fid_guide, 'Fuzzy_PID_Calculator 输出连接：\n');
    fprintf(fid_guide, '  输出1: u            → Controller_Selector (第3输入)\n');
    fprintf(fid_guide, '  输出2: e_int        → Memory_Integral (输入)\n\n');
    
    fprintf(fid_guide, '重要提示：\n');
    fprintf(fid_guide, '  1. Memory_Integral形成积分反馈回路\n');
    fprintf(fid_guide, '  2. 所有Constant模块提供固定参数\n');
    fprintf(fid_guide, '  3. Demux用于分离模糊控制器的3个输出\n\n');
    
    fclose(fid_guide);
    
    % 打开文本编辑器显示指南
    edit(guide_file);
    fprintf('✓ 连接指南已打开\n');
end

fprintf('\n脚本执行完毕！\n');

%% END OF SCRIPT