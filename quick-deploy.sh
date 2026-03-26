#!/bin/bash
# 快速部署脚本 - 在 Termux 中运行

echo "======================================"
echo "贷款客户引流助手 - 快速部署"
echo "======================================"

# 检查是否在 Termux 中运行
if [ -z "$PREFIX" ]; then
    echo "❌ 请在 Termux 应用中运行此脚本"
    exit 1
fi

echo "✅ 检测到 Termux 环境"

# 更新包管理器
echo "\n📦 更新系统包..."
pkg update -y
pkg upgrade -y

# 安装 Python
echo "\n🐍 安装 Python..."
pkg install python -y

# 安装依赖
echo "\n📚 安装 Python 依赖..."
pip install requests beautifulsoup4 lxml pillow schedule aiohttp qrcode

# 创建项目目录
echo "\n📁 创建项目目录..."
mkdir -p /sdcard/Download/loan-assistant
cd /sdcard/Download/loan-assistant

# 提示用户复制文件
echo "\n======================================"
echo "✅ 环境准备完成！"
echo "======================================"
echo "\n下一步："
echo "1. 将项目文件复制到此目录：/sdcard/Download/loan-assistant"
echo "2. 运行：python main.py"
echo "3. 输入你的微信号"
echo "4. 选择运行模式"
echo "\n项目文档："
echo "- 使用说明：README.md"
echo "- 安装指南：INSTALL.md"
echo "- APK 打包：APK_BUILD.md"
echo "======================================"
