# ElderGuard 非侵入式老人监护

以 PIR、温湿度与按钮等非摄像传感输入建立老人日常活动基线，提供分级提示与本地可视化。

**性质**：树莓派综合课程项目。

## 功能与实现

- `core/` 分为传感、SQLite、行为分析与报警模块，`main.py` 协调运行。
- 按时段历史活动构建行为基线，包含冷启动与默认阈值策略。
- Tkinter 展示当前状态，pyecharts 生成环境/活动/报警报表。
- 保留报警、分析、传感相关测试文件，另附 Adafruit DHT 传感实现候选版本。

## 目录与入口

- `alternatives/sensor_adafruit_dht.py`
- `config.py`
- `core/__init__.py`
- `core/alarm.py`
- `core/analyzer.py`
- `core/database.py`
- `core/sensor.py`
- `main.py`
- `requirements.txt`
- `sql/init_db.sql`
- `start.sh`
- `test.py`
- `tests/__init__.py`
- `tests/test_alarm.py`
- `tests/test_analyzer.py`
- `tests/test_sensor.py`
- `ui/__init__.py`
- `ui/dashboard.py`
- 其余文件见当前目录（共 22 个源码/设计文件）。

## 环境与运行

仅在目标树莓派环境安装硬件依赖；数据目录在运行时创建或按 `sql/init_db.sql` 初始化，不从仓库获取真实健康或活动记录。

使用独立 Python 3 环境；先检查串口、摄像头或 GPIO 等外设配置。

```bash
python -m pip install -r requirements.txt
python main.py
```

在真实树莓派配置 BOARD/BCM 引脚后运行。默认 `core/sensor.py` 依赖 `dht11`；`alternatives/sensor_adafruit_dht.py` 是另一个传感驱动版本，不能直接同时加载。通知 Webhook 需自行配置。数据库初始化脚本置于 `sql/`。

## 验证范围与复现说明

- 未上传真实传感记录、数据库与 Webhook；测试文件需要对应硬件或可替换驱动。
- 历史基线窗口与报警时段属于配置，不直接代表误报率或临床有效性。
- 默认驱动和替代驱动依赖不同，先选择一种并核对引脚。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
