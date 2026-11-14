# 物联网模块 4：HTTP/MQTT 云端数据传输

HTTP/MQTT 云端数据传输 的课程实现与操作记录。

**性质**：物联网应用系统分项实验。

## 功能与实现

- HTTP/MQTT 云端数据传输。
- 模块 6 的视觉程序和模块 7 的训练脚本分别见 projects/yolo-vision-apps 与 projects/gesture-yolo。

## 目录与入口

- `DESIGN_NOTES.md`
- `HttpConnect/OnenetConnect.py`
- `MqttConnect/mqttnew.py`
- `iot_host_app.py`
- `requirements.txt`

## 环境与运行

使用独立 Python 3 环境；先检查串口、摄像头或 GPIO 等外设配置。

```bash
python -m pip install -r requirements.txt
python iot_host_app.py
```



## 验证范围与复现说明

- 云平台和邮箱授权信息在发布副本中已替换；必须使用自己的产品、设备和凭据。
- 平台截图、调试账号、个人文档与课程安装包不发布。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../../README.md)
