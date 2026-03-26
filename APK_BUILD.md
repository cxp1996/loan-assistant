# 贷款客户引流助手 - APK 打包指南

## 方法一：使用 Buildozer（推荐，需要 Linux/Mac）

### 环境要求
- Ubuntu 20.04+ 或 macOS
- Python 3.8+
- 至少 10GB 可用空间
- 稳定的网络连接（需要下载 Android SDK）

### 安装步骤

```bash
# 1. 安装依赖
sudo apt-get update
sudo apt-get install -y git zip libssl-dev libffi-dev \
    python3-dev python3-pip libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libgstreamer1.0 \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    openjdk-11-jdk autoconf automake build-essential

# 2. 安装 Buildozer
pip3 install buildozer

# 3. 进入项目目录
cd loan-assistant

# 4. 运行打包脚本
chmod +x build-apk.sh
./build-apk.sh
```

### 输出
- APK 文件位置：`bin/loanassistant-1.0.0-debug.apk`
- 可直接安装到安卓手机

---

## 方法二：在线打包服务（无需本地环境）

### 使用 Kivy Build Service

1. 访问：https://kivy.org/#download
2. 注册账号
3. 上传项目代码
4. 选择构建配置
5. 等待构建完成并下载 APK

### 使用 GitHub Actions（自动化）

创建 `.github/workflows/build-apk.yml`：

```yaml
name: Build APK

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install Buildozer
        run: |
          pip install buildozer
          sudo apt-get install -y git zip libssl-dev libffi-dev \
            python3-dev python3-pip libsdl2-dev libsdl2-image-dev \
            libsdl2-mixer-dev libsdl2-ttf-dev
      
      - name: Build APK
        run: |
          buildozer android debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v2
        with:
          name: app-apk
          path: bin/*.apk
```

---

## 方法三：使用 Termux 直接运行（最简单）

如果不想打包成 APK，可以直接在 Termux 中运行：

```bash
# 在 Termux 中执行
pkg update && pkg upgrade
pkg install python
pip install requests beautifulsoup4 lxml pillow schedule aiohttp qrcode

# 运行程序
cd /sdcard/Download/loan-assistant
python main.py
```

**优势：**
- 无需编译，立即使用
- 方便调试和修改
- 占用空间小

**劣势：**
- 需要 Termux 环境
- 不能独立运行

---

## APK 安装说明

1. **传输 APK 到手机**
   - 通过 USB 连接电脑
   - 通过微信/QQ 发送文件
   - 通过云盘下载

2. **安装 APK**
   - 在手机设置中允许"未知来源应用"
   - 点击 APK 文件安装
   - 授予必要权限（存储、网络）

3. **首次运行**
   - 打开应用
   - 输入微信号
   - 选择运行模式
   - 开始工作

---

## 常见问题

### Q: Buildozer 下载 Android SDK 失败？
A: 检查网络连接，或使用国内镜像：
```bash
export ANDROID_HOME_MIRROR=https://mirrors.cloud.tencent.com/android
```

### Q: 构建时内存不足？
A: 增加 swap 空间或关闭其他程序：
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Q: APK 安装后闪退？
A: 检查日志：
```bash
adb logcat | grep loanassistant
```

---

## 推荐方案

| 方案 | 难度 | 时间 | 推荐场景 |
|------|------|------|----------|
| Termux 运行 | ⭐ | 5 分钟 | 个人使用、快速测试 |
| Buildozer 本地打包 | ⭐⭐⭐ | 1-2 小时 | 正式部署、分发 |
| GitHub Actions | ⭐⭐ | 30 分钟 | 持续集成、自动构建 |

**建议：** 先用 Termux 测试功能，确认无误后再打包成 APK。
