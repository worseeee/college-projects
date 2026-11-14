# 下肢外骨骼康复控制仿真

围绕膝关节单自由度动力学，在仿真环境中组织专家 PID、模糊 PID、RBF、PSO 和分析脚本。

**性质**：MATLAB/Simulink 综合设计 · 尚需模型复验。

## 功能与实现

- `plant/` 建模，`controllers/` 实现控制 S-Function。
- `fis/` 与根目录 FIS 文件组织模糊推理规则。
- `optimization/run_pso.m`、`analysis/` 提供优化和结果分析入口。

## 目录与入口

- `analysis/compare_results.m`
- `analysis/ilc_analysis.m`
- `controllers/expert_pid_sfunc.m`
- `controllers/rbf_controller_sfunc.m`
- `exo_rehab_system.slx`
- `final_fix_fuzzy.m`
- `final_setup.m`
- `fis/design_fis.m`
- `fis/knee_fuzzy_pid.fis`
- `knee_fuzzy_pid.fis`
- `optimization/run_pso.m`
- `plant/knee_joint_sfunc.m`
- `utils/init_plant.m`

## 环境与运行

在 MATLAB 中将当前项目加入路径，查看并执行 `utils/init_plant.m`、`final_setup.m` 等初始化脚本，再打开 `exo_rehab_system.slx`。需要 Simulink、Fuzzy Logic 及脚本实际使用的工具箱。模型中的旧本地路径需先更新。

## 验证范围与复现说明

- 保存的原配置报告曾记录模型编译失败；此次整理未运行 MATLAB 复验，不宣称全流程仿真通过。
- 未发布生成的 MAT 工作区、Simulink 缓存、工具箱示例全集或实机控制结果。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
