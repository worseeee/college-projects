# CC2530 10-2A模块测温--无线给B模块--PC程序显示--控制A模块继电器

围绕 10-2A模块测温--无线给B模块--PC程序显示--控制A模块继电器 保留单片机或 ZigBee 应用层实验。

**性质**：无线传感网分项实验。

## 功能与实现

- 应用入口、外设读写或 ZigBee 消息处理见当前目录。
- Z-Stack 实验仅提供应用层覆盖文件，保留 TI 原始注释与接口。

## 目录与入口

- `application/DHT11.c`
- `application/DHT11.h`
- `application/GenericApp.h`
- `application/coordinator.c`
- `application/ds18b20.c`
- `application/ds18b20.h`
- `application/enddevice.c`

## 环境与运行

使用 IAR for 8051 打开本目录工程配置（若提供），并安装目标芯片及课程板卡对应的依赖。仅发布应用层文件时，将其合并回原厂 SDK 的同名应用目录后再构建。不要把应用源码目录直接当成完整厂商 SDK。

## C# 上位机

`pc-client/` 保留对应课程客户端的 C#、Designer、资源与工程文件。用支持原工程目标 .NET Framework 的 Visual Studio 打开 sln/csproj，并安装对应目标框架；在窗体选择实际协调器串口。bin、obj、运行程序和用户 IDE 配置未发布。课程提供/改编的客户端保留学习示例性质。

## 验证范围与复现说明

- 不发布 TI 完整协议栈、预编译库、下载工具和 PC 二进制程序。
- 有些原实验仅保留说明或工具配置，空源码目录会明确按文档记录展示。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../../../README.md)
