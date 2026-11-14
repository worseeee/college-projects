# STM32F4 环境监测与分级报警

基于 STM32F407 开发板板载资源，整合 ADC/DAC、按键、中断、定时器、LCD 和分级报警。

**性质**：嵌入式综合课程设计。

## 功能与实现

- `HARDWARE/FINAL` 分离采样、阈值、显示、按键、报警与定时逻辑。
- 前后台结构中，中断置标志，主循环完成主要业务。
- 片内温度及光照采集、均值滤波、阈值调节、DAC 输出与 ADC 回读检查。
- 保留单项硬件驱动练习，便于追溯综合项目的外设来源。

## 目录与入口

- `firmware/HARDWARE/ADC/ADC.c`
- `firmware/HARDWARE/ADC/TEMP.c`
- `firmware/HARDWARE/ADC/adc.h`
- `firmware/HARDWARE/ADC/temp.h`
- `firmware/HARDWARE/BEEP/BEEP.c`
- `firmware/HARDWARE/BEEP/beep.h`
- `firmware/HARDWARE/DAC/DAC.c`
- `firmware/HARDWARE/DAC/dac.h`
- `firmware/HARDWARE/EXTI/EXTI.c`
- `firmware/HARDWARE/EXTI/exti.h`
- `firmware/HARDWARE/FINAL/ALARM.c`
- `firmware/HARDWARE/FINAL/KEY_monitor.c`
- `firmware/HARDWARE/FINAL/LCD_monitor.c`
- `firmware/HARDWARE/FINAL/PERIPH.c`
- `firmware/HARDWARE/FINAL/SENSOR.c`
- `firmware/HARDWARE/FINAL/THRESHOLD.c`
- `firmware/HARDWARE/FINAL/TIMER.c`
- `firmware/HARDWARE/FINAL/monitor.h`
- 其余文件见当前目录（共 35 个源码/设计文件）。

## 环境与运行

使用 Keil MDK / STM32F407 标准外设库 打开本目录工程配置（若提供），并安装目标芯片及课程板卡对应的依赖。仅发布应用层文件时，将其合并回原厂 SDK 的同名应用目录后再构建。不要把应用源码目录直接当成完整厂商 SDK。

## 验证范围与复现说明

- 未打包 CMSIS、STM32 标准外设库、完整板级 SYSTEM 依赖和编译输出，需按原开发板工程补齐。
- 温度输入为 MCU 片内温度传感器，不能直接等同于已校准的室内空气温度。
- 保留驱动中的课程/厂商原始标注，不将底层示例整体声明为个人原创。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
