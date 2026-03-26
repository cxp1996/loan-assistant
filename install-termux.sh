#!/data/data/com.termux/files/usr/bin/bash

# 贷款客户引流助手 - Termux 一键安装脚本
# 使用方法：bash install-termux.sh

echo "=========================================="
echo "  贷款客户引流助手 - Termux 安装脚本"
echo "=========================================="
echo ""

# 检查是否在 Termux 中运行
if [ ! -d "/data/data/com.termux" ]; then
    echo "❌ 错误：请在 Termux 应用中运行此脚本！"
    exit 1
fi

echo "✅ 检测到 Termux 环境"
echo ""

# 步骤 1：更新包
echo "📦 步骤 1/5: 更新包列表..."
pkg update -y && pkg upgrade -y

# 步骤 2：安装系统依赖
echo ""
echo "📦 步骤 2/5: 安装系统依赖..."
pkg install -y python python-pip libjpeg-turbo freetype libpng libxml2 libxslt openssl clang llvm make cmake

# 步骤 3：安装 SDL2 依赖（用于 Kivy）
echo ""
echo "📦 步骤 3/5: 安装 SDL2 图形库..."
pkg install -y sdl2 sdl2_image sdl2_ttf sdl2_mixer

# 步骤 4：设置存储访问
echo ""
echo "📦 步骤 4/5: 设置存储访问..."
termux-setup-storage

# 步骤 5：安装 Python 依赖
echo ""
echo "📦 步骤 5/5: 安装 Python 依赖..."

# 检查 requirements.txt 是否存在
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️ 未找到 requirements.txt，手动安装依赖..."
    pip install requests beautifulsoup4 lxml pillow schedule aiohttp qrcode kivy
fi

echo ""
echo "=========================================="
echo "  ✅ 安装完成！"
echo "=========================================="
echo ""
echo "📱 运行程序："
echo "   python main.py"
echo ""
echo "📂 项目位置：$(pwd)"
echo ""
echo "⚠️  提示："
echo "   1. 首次运行可能需要几分钟初始化"
echo "   2. 确保手机有网络连接"
echo "   3. 授予存储权限以保存数据"
echo ""
