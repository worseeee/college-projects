# 摄像头、车辆与人流检测应用

保留摄像头 GUI、车辆检测、人流检测及 YOLO 视觉程序的多个课程迭代版本。

**性质**：物联网目标检测模块实验。

## 功能与实现

- Tkinter/OpenCV 摄像头操作与截图流程。
- CamerawithCar、CamerawithCrowd、CamerawithYolo 按场景组织检测代码。
- 人流相关目录包含单窗口/双窗口等界面版本。

## 目录与入口

- `CamerawithCar/camera.py`
- `CamerawithCrowd/camera.py`
- `CamerawithCrowd/cameradoublewindow.py`
- `CamerawithYolo/camera.py`
- `camera.py`
- `camera_app.py`
- `requirements.txt`

## 环境与运行

使用独立 Python 3 环境；先检查串口、摄像头或 GPIO 等外设配置。

```bash
python -m pip install -r requirements.txt
python camera_app.py
```

子程序分别在各自目录运行 `camera.py` 或 `cameradoublewindow.py`。需要自行准备源码指定的 YOLO 权重、视频输入与设备配置。

## 验证范围与复现说明

- 没有独立评测数据或训练权重，不宣称检测准确率或实际处理 FPS。
- 本项目也包含云端接入的课程代码；使用前填写自己的授权参数。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
