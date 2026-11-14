# YOLO 手势训练与摄像头推理

包含手势图片/标签划分、YOLOv8 微调及单图/实时摄像头推理脚本，数据与训练结果自行准备。

**性质**：目标检测训练模块实验。

## 功能与实现

- `split_data.py` 随机按 8:2 划分图片和标签。
- `train_yolo.py` 配置 50 epochs、640 输入尺寸、batch 16。
- `run_my_ai.py` 从训练输出读取 best.pt，并提供单图或摄像头推理。

## 目录与入口

- `dataset.example.yaml`
- `requirements.txt`
- `run_my_ai.py`
- `split_data.py`
- `train_yolo.py`

## 环境与运行

先准备获得授权的图片与 YOLO 标签，定义真实类别并将配置保存为 `dataset/data.yaml`。

```bash
python -m pip install -r requirements.txt
python split_data.py
python train_yolo.py
python run_my_ai.py
```

`split_data.py` 使用 `shutil.move` 移动图片/标签，请先备份数据，并检查源文件支持的图片扩展名。

## 验证范围与复现说明

- 未上传手势图片、标签、模型权重和 runs/；示例 YAML 类别只是占位，不是原训练标签定义。
- 50 epochs 等是训练参数，不是精度证明；尚需独立验证集与测试集评估。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
