# 构建配置 - 使用 Buildozer 打包成 APK

[app]

# 应用标题
title = 贷款客户引流助手

# 包名
package.name = loanassistant

# 版本号
version = 1.0.0

# 作者
author = Your Name

# 最小 Android 版本
android.minapi = 24

# 目标 Android 版本
android.api = 28

# Python 版本
python.version = 3.8

# 入口脚本
source.dir = .

# 入口点
orientation = portrait

# 需要的权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 需要的 Python 依赖
# 移除 sdl2_image/sdl2_mixer/sdl2_ttf 以避免 Google 服务器依赖
# Kivy 使用纯 Python 图像支持
requirements = python3,requests,beautifulsoup4,schedule,aiohttp,sqlite3,kivy,pyjnius

# 应用图标
icon.filename = %(source.dir)s/icon.png

# 启动画面
splash.filename = %(source.dir)s/splash.png

# 是否全屏
android.fullscreen = True

# 是否显示状态栏
android.show_status_bar = True

# 应用后台服务（用于定时任务）
android.service_foreground = True

# 唤醒锁（保持后台运行）
android.wakelock = True

[buildozer]

# 构建目录
build_dir = ./.buildozer

# bin 目录
bin_dir = ./bin

# 使用本地 python-for-android 源目录（避免重复克隆）
p4a.source_dir = /home/admin/openclaw/workspace/loan-assistant/.buildozer/android/platform/python-for-android

# pip 国内镜像
pip.index_url = https://pypi.tuna.tsinghua.edu.cn/simple
pip.trusted_host = pypi.tuna.tsinghua.edu.cn

# 使用国内镜像下载 Android SDK 和 Cython 等
buildozer.download_source_mirror = https://mirrors.cloud.tencent.com 
