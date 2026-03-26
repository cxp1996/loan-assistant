# APK 打包完整指南 - 贷款客户引流助手

## 打包方式选择

### 方式一：本地打包（Linux/Mac，推荐）
- **优点**：完全控制，可调试
- **缺点**：需要配置环境
- **时间**：首次 1-2 小时，后续 30 分钟

### 方式二：GitHub Actions（云端自动打包）
- **优点**：无需本地环境，自动化
- **缺点**：需要 GitHub 账号
- **时间**：配置 30 分钟，构建 40 分钟

### 方式三：远程服务器打包
- **优点**：不占用本地资源
- **缺点**：需要服务器
- **时间**：1 小时

---

## 方式一：本地打包（Ubuntu 20.04+）

### 步骤 1：安装系统依赖

```bash
# 更新系统
sudo apt-get update

# 安装基础依赖
sudo apt-get install -y \
    git zip unzip \
    libssl-dev libffi-dev \
    python3-dev python3-pip \
    libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    openjdk-11-jdk \
    autoconf automake build-essential \
    wget curl
```

### 步骤 2：安装 Buildozer

```bash
# 安装 Buildozer
pip3 install buildozer

# 验证安装
buildozer --version
```

### 步骤 3：准备项目

```bash
# 进入项目目录
cd loan-assistant

# 确保配置文件正确
# 编辑 buildozer.spec，修改包名和作者信息
nano buildozer.spec
```

修改以下字段：
```
title = 贷款客户引流助手
package.name = loanassistant
version = 1.0.0
author = 你的名字
```

### 步骤 4：开始打包

```bash
# 初始化 Buildozer（首次运行会下载 Android SDK）
buildozer init

# 开始构建（下载 SDK/NDK 需要时间）
buildozer -v android debug

# 或使用打包脚本
chmod +x build-apk.sh
./build-apk.sh
```

### 步骤 5：获取 APK

构建完成后，APK 文件位置：
```
bin/loanassistant-1.0.0-debug.apk
```

---

## 方式二：GitHub Actions 云端打包

### 步骤 1：创建 GitHub 仓库

1. 访问 https://github.com
2. 创建新仓库 `loan-assistant`
3. 上传项目所有文件

### 步骤 2：配置 GitHub Actions

创建文件 `.github/workflows/build-apk.yml`：

```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:  # 允许手动触发

jobs:
  build:
    runs-on: ubuntu-20.04
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      
      - name: Set up Python 3.8
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install buildozer cython
      
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            git zip unzip \
            libssl-dev libffi-dev \
            python3-dev python3-pip \
            libsdl2-dev libsdl2-image-dev \
            libsdl2-mixer-dev libsdl2-ttf-dev \
            libgstreamer1.0-dev \
            gstreamer1.0-plugins-base \
            gstreamer1.0-plugins-good \
            openjdk-11-jdk \
            autoconf automake build-essential \
            wget curl
      
      - name: Build APK
        run: |
          buildozer android debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v2
        with:
          name: app-apk
          path: bin/*.apk
```

### 步骤 3：触发构建

1. 提交代码到 GitHub
2. 进入 Actions 标签页
3. 选择 "Build Android APK"
4. 点击 "Run workflow"
5. 等待构建完成（约 40 分钟）
6. 下载生成的 APK

---

## 方式三：使用预配置虚拟机（最简单）

### 使用 Docker 镜像

```bash
# 拉取预配置的 Buildozer 镜像
docker pull kivy/buildozer

# 运行构建
docker run --rm -v $(pwd):/home/user/hostcwd kivy/buildozer android debug
```

### 使用 Vagrant 虚拟机

```bash
# 安装 Vagrant
# 访问 https://www.vagrantup.com/downloads

# 初始化 Ubuntu 虚拟机
vagrant init ubuntu/focal64
vagrant up

# SSH 进入虚拟机
vagrant ssh

# 在虚拟机中执行打包
cd /vagrant
buildozer android debug
```

---

## 常见问题解决

### 问题 1：Android SDK 下载失败

**错误信息**：
```
ERROR: Failed to download Android SDK
```

**解决方案**：
```bash
# 使用国内镜像
export ANDROID_HOME_MIRROR=https://mirrors.cloud.tencent.com/android
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 手动下载 SDK 工具
wget https://dl.google.com/android/repository/commandlinetools-linux-6858069_latest.zip
unzip commandlinetools-linux-6858069_latest.zip
mkdir -p $HOME/.buildozer/android/platform/android-sdk/cmdline-tools
mv cmdline-tools $HOME/.buildozer/android/platform/android-sdk/cmdline-tools/latest
```

### 问题 2：内存不足

**错误信息**：
```
Java heap space error
```

**解决方案**：
```bash
# 增加 swap 空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 验证
free -h
```

### 问题 3：构建卡在某个步骤

**解决方案**：
```bash
# 查看详细日志
buildozer -v android debug 2>&1 | tee build.log

# 如果卡住，按 Ctrl+C 停止
# 查看日志最后部分
tail -100 build.log

# 清理并重新构建
buildozer android clean
buildozer android debug
```

### 问题 4：APK 安装失败

**错误信息**：
```
App not installed
```

**解决方案**：
1. 检查安卓版本是否兼容（最低 Android 7.0）
2. 卸载旧版本后重新安装
3. 检查 APK 是否完整：
```bash
ls -lh bin/*.apk
```

---

## APK 安装与测试

### 传输到手机

**方法 1：USB 传输**
```bash
# 手机连接电脑，开启文件传输
# 复制 APK 到手机下载目录
cp bin/loanassistant-1.0.0-debug.apk /media/phone/Download/
```

**方法 2：网络传输**
```bash
# 使用 Python 快速搭建 HTTP 服务器
cd bin
python3 -m http.server 8000

# 手机浏览器访问：http://<电脑IP>:8000
# 下载 APK
```

**方法 3：微信/QQ 传输**
- 发送 APK 文件到微信/QQ
- 在手机上下载

### 安装步骤

1. 手机设置 → 安全 → 允许"未知来源"
2. 点击 APK 文件
3. 点击"安装"
4. 授予权限（存储、网络）

### 首次运行

1. 打开应用
2. 输入微信号
3. 选择"定时任务模式"
4. 开始自动运行

---

## 打包优化建议

### 1. 减小 APK 体积

修改 `buildozer.spec`：
```
# 只包含需要的架构
android.archs = arm64-v8a, armeabi-v7a

# 启用代码压缩
android.release_artifact = apk
```

### 2. 签名 APK（正式发布）

```bash
# 生成签名密钥
keytool -genkey -v -keystore loan-assistant.keystore -alias loanassistant -keyalg RSA -keysize 2048 -validity 10000

# 签名 APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore loan-assistant.keystore bin/loanassistant-1.0.0-release-unsigned.apk loanassistant

# 对齐优化
zipalign -v 4 bin/loanassistant-1.0.0-release-unsigned.apk bin/loanassistant-1.0.0-release.apk
```

### 3. 自定义图标

准备 512x512 PNG 图片，命名为 `icon.png`，放在项目根目录。

### 4. 自定义启动图

准备 1920x1080 PNG 图片，命名为 `splash.png`，放在项目根目录。

---

## 打包检查清单

- [ ] 系统依赖已安装
- [ ] Buildozer 已安装
- [ ] Java JDK 已安装（11 或更高）
- [ ] 项目配置文件正确
- [ ] 网络连接正常
- [ ] 磁盘空间充足（至少 10GB）
- [ ] APK 构建成功
- [ ] APK 可正常安装
- [ ] 应用可正常运行

---

## 需要帮助？

如果遇到任何问题，请提供：
1. 操作系统版本
2. 错误日志（最后 50 行）
3. 已尝试的解决方案

我会帮你解决。
