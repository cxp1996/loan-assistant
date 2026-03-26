#!/bin/bash
# Termux 一键部署脚本
# 在 Termux 中运行：curl <地址> | bash

set -e

echo "========================================"
echo "  贷款客户引流助手 - Termux 快速部署"
echo "========================================"
echo ""

# 检查是否在 Termux 中
if [ -z "$PREFIX" ]; then
    echo "❌ 错误：请在 Termux 应用中运行此脚本"
    echo "   下载地址：https://f-droid.org/packages/com.termux/"
    exit 1
fi

echo "✅ 检测到 Termux 环境"
echo ""

# 步骤 1: 更新系统
echo "📦 [1/5] 更新系统包..."
pkg update -y
pkg upgrade -y

# 步骤 2: 安装 Python
echo "🐍 [2/5] 安装 Python..."
pkg install python wget curl nano git -y

# 步骤 3: 安装依赖
echo "📚 [3/5] 安装 Python 依赖..."
pip install --upgrade pip
pip install requests beautifulsoup4 lxml pillow schedule aiohttp qrcode

# 步骤 4: 创建项目目录
echo "📁 [4/5] 创建项目目录..."
mkdir -p /sdcard/Download/loan-assistant
cd /sdcard/Download/loan-assistant

# 步骤 5: 下载项目文件
echo "📥 [5/5] 下载项目文件..."

# 检查是否有 git
if command -v git &> /dev/null; then
    echo "使用 Git 克隆..."
    # 如果有 Git 仓库，取消注释下一行
    # git clone <仓库地址> .
    echo "⚠️  请手动设置 Git 仓库地址，或使用方法 B 手动创建文件"
else
    echo "Git 未安装，使用方法 B 手动创建文件"
fi

# 显示完成信息
echo ""
echo "========================================"
echo "  ✅ 环境准备完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo ""
echo "1️⃣  将项目文件复制到此目录："
echo "   /sdcard/Download/loan-assistant"
echo ""
echo "2️⃣  编辑配置文件："
echo "   nano config/settings.json"
echo "   修改微信号为你的实际微信号"
echo ""
echo "3️⃣  运行程序："
echo "   python main.py"
echo ""
echo "4️⃣  选择运行模式（推荐模式 2：定时任务）"
echo ""
echo "========================================"
echo ""
echo "📖 详细文档："
echo "   - TERMUX_RUN.md - Termux 运行指南"
echo "   - README.md - 项目说明"
echo "   - INSTALL.md - 安装指南"
echo ""
echo "💡 提示：使用 tmux 可以后台运行程序"
echo "   pkg install tmux -y"
echo "   tmux new -s loan"
echo "========================================"
