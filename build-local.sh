#!/bin/bash
# 本地构建脚本 - 使用已克隆的 Gitee 镜像

# 设置环境变量
export P4A_SOURCE_DIR=/home/admin/openclaw/workspace/loan-assistant/.buildozer/android/platform/python-for-android

# 确保目录存在
if [ ! -d "$P4A_SOURCE_DIR" ]; then
    echo "克隆 Gitee 镜像..."
    cd /home/admin/openclaw/workspace/loan-assistant/.buildozer/android/platform
    git clone -b master https://gitee.com/mirrors/python-for-android.git
fi

# 运行 buildozer
buildozer -v android debug
