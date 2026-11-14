#!/bin/bash
# ElderGuard 系统启动脚本

echo "====================================="
echo "ElderGuard 独居老人监护系统"
echo "====================================="
echo ""

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "检测到 Python 版本: $python_version"

# 检查是否以root权限运行（GPIO需要）
if [ "$EUID" -ne 0 ]; then 
    echo "错误: 请使用 sudo 运行此脚本"
    echo "使用方式: sudo bash start.sh"
    exit 1
fi

# 检查依赖包
echo ""
echo "检查依赖包..."
pip3 show RPi.GPIO >/dev/null 2>&1 || { echo "安装 RPi.GPIO..."; pip3 install RPi.GPIO; }
pip3 show Adafruit-DHT >/dev/null 2>&1 || { echo "安装 Adafruit-DHT..."; pip3 install Adafruit-DHT; }
pip3 show pyecharts >/dev/null 2>&1 || { echo "安装 pyecharts..."; pip3 install pyecharts; }
pip3 show requests >/dev/null 2>&1 || { echo "安装 requests..."; pip3 install requests; }

# 创建必要目录
echo ""
echo "创建数据目录..."
mkdir -p data
mkdir -p output/reports
mkdir -p output/logs

# 启动系统
echo ""
echo "====================================="
echo "启动 ElderGuard 系统..."
echo "====================================="
echo ""

python3 main.py

echo ""
echo "系统已退出"