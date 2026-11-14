# 华为云 MQTT C# 设备接入示例

按课程保留的 C# WinForms 示例连接 MQTT 设备端，用于理解设备鉴权、上下行消息与可视化调试。

**性质**：课程参考示例 / 非独立原创 SDK。

## 功能与实现

- 保留 FrmMqttDemo、Program、Utility 及 WinForms Designer/资源文件。
- MQTTnet 与 ManagedClient 通过原 packages.config 恢复，不打包 NuGet 依赖目录。
- 账号、密钥及用户本机配置在公开副本中替换；原示例来源与使用范围应以课程和原 SDK 许可为准。

## 目录与入口

- `device_demo_mqttnet/App.config`
- `device_demo_mqttnet/FrmMqttDemo.Designer.cs`
- `device_demo_mqttnet/FrmMqttDemo.cs`
- `device_demo_mqttnet/FrmMqttDemo.en-US.resx`
- `device_demo_mqttnet/FrmMqttDemo.resx`
- `device_demo_mqttnet/FrmMqttDemo.zh-CN.resx`
- `device_demo_mqttnet/Program.cs`
- `device_demo_mqttnet/Properties/AssemblyInfo.cs`
- `device_demo_mqttnet/Properties/Resources.Designer.cs`
- `device_demo_mqttnet/Properties/Resources.resx`
- `device_demo_mqttnet/Properties/Settings.Designer.cs`
- `device_demo_mqttnet/Properties/Settings.settings`
- `device_demo_mqttnet/Utility/EncryptUtil.cs`
- `device_demo_mqttnet/Utility/MultiLanguage.cs`
- `device_demo_mqttnet/device_demo_mqttnet.csproj`
- `device_demo_mqttnet/packages.config`
- `huaweicloud-iot-device-csharp-demo.sln`

## 环境与运行

使用支持原目标 .NET Framework 的 Visual Studio 打开 sln/csproj，恢复 packages.config 指定的 NuGet 包。先建立自己的云平台产品/设备，并填写自己的端点和鉴权参数，再运行窗体调试。

## 验证范围与复现说明

- 该目录为课堂引用/改编的设备接入示例，不声明为个人原创云平台或完整华为云 SDK。
- 没有上传 packages、bin、obj、证书、云端账号或可执行程序。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
