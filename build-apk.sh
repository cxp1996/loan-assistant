#!/bin/bash
# APK 打包脚本
# 在 Linux/Mac 环境下运行，需要安装 Buildozer

set -e

echo "======================================"
echo "贷款客户引流助手 - APK 打包脚本"
echo "======================================"

# 检查 Buildozer 是否安装
if ! command -v buildozer &> /dev/null; then
    echo "正在安装 Buildozer..."
    pip install buildozer
fi

# 检查依赖
echo "检查依赖..."
pip install -r requirements.txt

# 初始化 Buildozer（如果尚未初始化）
if [ ! -f buildozer.spec ]; then
    echo "创建 buildozer.spec 配置文件..."
    # 配置文件已存在，跳过
fi

# 下载 Android SDK 和 NDK（如果需要）
echo "准备 Android 构建环境..."
buildozer android setup

# 清理之前的构建
echo "清理之前的构建..."
buildozer android clean

# 开始构建
echo "开始构建 APK..."
buildozer -v android debug

# 构建完成
echo ""
echo "======================================"
echo "✅ APK 构建完成！"
echo "输出位置：bin/*.apk"
echo "======================================"

# 列出输出的 APK
echo ""
echo "生成的 APK 文件:"
ls -lh bin/*.apk 2>/dev/null || echo "未找到 APK 文件"
