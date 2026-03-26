#!/bin/bash
# Windows WSL2 一键打包脚本
# 在 Ubuntu 中运行：bash build-windows.sh

set -e

echo "========================================"
echo "  贷款客户引流助手 - APK 打包脚本"
echo "  (Windows WSL2 版本)"
echo "========================================"
echo ""

# 检查是否在 WSL 中
if grep -qi microsoft /proc/version; then
    echo "✅ 检测到 WSL 环境"
else
    echo "⚠️  未在 WSL 中运行，可能遇到问题"
fi

# 步骤 1：安装依赖
echo ""
echo "📦 [1/5] 安装系统依赖..."
sudo apt-get update
sudo apt-get install -y git zip unzip python3-pip openjdk-11-jdk wget curl cmake

# 步骤 2：安装 Buildozer
echo ""
echo "🐍 [2/5] 安装 Buildozer..."
pip3 install buildozer cython

# 验证安装
if command -v buildozer &> /dev/null; then
    echo "✅ Buildozer 安装成功"
else
    echo "❌ Buildozer 安装失败"
    exit 1
fi

# 步骤 3：准备项目
echo ""
echo "📁 [3/5] 准备项目文件..."

# 检查项目文件
if [ ! -f "main.py" ]; then
    echo "❌ 未找到 main.py，请确保在项目目录下运行"
    exit 1
fi

if [ ! -f "buildozer.spec" ]; then
    echo "⚠️  未找到 buildozer.spec，创建默认配置..."
    buildozer init
fi

# 步骤 4：开始打包
echo ""
echo "🚀 [4/5] 开始打包 APK..."
echo "   首次运行需要 30-90 分钟（下载 Android SDK/NDK）"
echo ""

# 使用国内镜像加速
export ANDROID_HOME_MIRROR=https://mirrors.cloud.tencent.com/android
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 开始构建
buildozer -v android debug

# 步骤 5：检查输出
echo ""
echo "📦 [5/5] 检查输出..."

if ls bin/*.apk 1> /dev/null 2>&1; then
    echo "✅ APK 打包成功！"
    echo ""
    echo "APK 文件位置:"
    ls -lh bin/*.apk
    echo ""
    
    # 复制到 Windows 目录
    WINDOWS_USER=$(whoami)
    WIN_PATH="/mnt/c/Users/$WINDOWS_USER/Downloads/"
    
    if [ -d "$WIN_PATH" ]; then
        cp bin/*.apk "$WIN_PATH"
        echo "✅ APK 已复制到 Windows 下载目录:"
        echo "   $WIN_PATH"
        echo ""
        echo "下一步："
        echo "1. 在 Windows 上找到 APK 文件"
        echo "2. 通过微信/USB 传到手机"
        echo "3. 在手机上安装"
    else
        echo "⚠️  无法访问 Windows 下载目录，请手动复制"
        echo "   APK 位置：$(pwd)/bin/*.apk"
    fi
else
    echo "❌ APK 打包失败，请检查日志"
    exit 1
fi

echo ""
echo "========================================"
echo "  ✅ 打包完成！"
echo "========================================"
