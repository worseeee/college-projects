# Undergraduate IoT & Edge AI Portfolio

本科物联网、嵌入式、边缘 AI 与课程实验项目集。以可审阅的源码、设计文件和复现说明展示技术路径；不同完成程度在各项目 README 中单独标注。

## 核心项目

| 项目 | 技术栈 | 实现重点 |
|---|---|---|
| [智守夕阳](projects/smartguardian/README.md) | ZigBee / Python / YOLOv8 / Ollama / MQTT | 事件触发视觉、5 类队列、云边协同 |
| [视觉小车](projects/vision-smart-car/README.md) | Raspberry Pi / TCP / OpenCV / GPIO | 视觉循迹、目标跟随、单线程电机仲裁 |
| [智能实验室设备管理](projects/smart-lab/README.md) | CC2530 / Z-Stack / UART / SQLite | 节点映射、帧校验、借还与告警 |
| [三轴运动控制台](projects/tri-axis-motion-console/README.md) | C++ / MFC / GTS-800 / gLink200 | 串行 SDK 调度、4 类轨迹、9 步自动流程 |

## 完整目录

- [全部项目与课程组索引](docs/PROJECT_INDEX.md)
- [发布范围、依赖与复现方式](docs/PUBLISHING_NOTES.md)
- [本次发布前静态检查](docs/VALIDATION.md)
- [来源与许可说明](NOTICE.md)

本次整理包含 **115 个项目/实验单元/文档记录**。每个单元都有对应 README；综合项目、基础练习、硬件设计和研究记录分目录保存。

## 如何使用

```bash
git clone https://github.com/worseeee/college-projects.git
cd college-projects
```

先打开目标目录的 README，再安装该目录需要的依赖。Python 硬件库、Windows MFC、MATLAB、Keil/IAR、Altium 与 Packet Tracer 环境互不通用，无需为整个仓库一次性安装所有依赖。

## 验证口径

源码中的采样/轮询周期、线程/队列数量和节点登记容量是实现配置；报告中的实车演示记录按单次课程记录表述。未提供独立测试的数据，不声明准确率、实际算法 FPS、端到端延迟、机械精度或量产可靠性。当前发布不附真实个人或业务数据。
