# RFID 天线参数与扫频可视化

用 PyQt5、NumPy 和 Matplotlib 将线圈参数、等效模型、频率响应与实验曲线对照集中到桌面界面。

**性质**：RFID 课程工具开发。

## 功能与实现

- `coilpro.py` 计算线圈等效参数及向量化扫频结果。
- `sim.py` 提供参数输入、嵌入式 Matplotlib 绘图和 CSV 曲线导入。
- `smith.py`、`uic.py` 提供配套界面/图表功能。

## 目录与入口

- `coilpro.py`
- `requirements.txt`
- `sim.py`
- `smith.py`
- `uic.py`

## 环境与运行

使用独立 Python 3 环境；先检查串口、摄像头或 GPIO 等外设配置。

```bash
python -m pip install -r requirements.txt
python sim.py
```

CSV 的频率与幅度等列格式需与导入函数一致；先用自行生成的样例验证列含义和单位。

## 验证范围与复现说明

- 属于等效模型与课程仿真工具，不替代电磁场全波仿真或仪器标定。
- 未上传打包后的 EXE、逆向解包目录、运行库和实验数据。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
