#!/bin/bash
# 一键部署到 GitHub 并触发 APK 构建

set -e

echo "🚀 贷款客户引流助手 - GitHub 部署脚本"
echo "========================================"

# 检查是否输入了 GitHub 用户名
if [ -z "$1" ]; then
    echo "用法：./deploy-to-github.sh <your-github-username>"
    echo "示例：./deploy-to-github.sh myusername"
    exit 1
fi

GITHUB_USER=$1
REPO_NAME="loan-assistant"
REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo ""
echo "📦 步骤 1/4: 清理构建缓存..."
buildozer android clean || true
rm -rf .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build
rm -rf .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists

echo ""
echo "📦 步骤 2/4: 添加 .gitignore..."
cat > .gitignore << 'EOF'
# Buildozer
.buildozer/android/platform/build-*
.buildozer/android/platform/apache-ant-*/bin/
.buildozer/android/platform/apache-ant-*/lib/
bin/
*.apk
*.aab
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

echo ""
echo "📦 步骤 3/4: 提交更改..."
git add -A
git commit -m "Build: 准备 GitHub Actions APK 构建" || echo "没有新更改"

echo ""
echo "📦 步骤 4/4: 推送到 GitHub..."
echo ""
echo "⚠️  请先在 GitHub 上创建仓库："
echo "   1. 访问 https://github.com/new"
echo "   2. 仓库名：${REPO_NAME}"
echo "   3. 设为 Public 或 Private 均可"
echo "   4. 不要初始化 README/.gitignore"
echo "   5. 点击 Create repository"
echo ""
echo "然后运行以下命令推送代码："
echo ""
echo "   git remote add origin ${REMOTE_URL}"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "推送后，GitHub Actions 会自动开始构建（约 40 分钟）"
echo "构建完成后在 Actions 标签页下载 APK"
echo ""
