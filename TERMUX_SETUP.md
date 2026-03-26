# 贷款客户引流助手 - Termux 运行指南

## ✅ 前提条件

你已经在 Termux 中安装了：
- Python 3.13.12
- pip 26.0.1
- clang, make, pkg-config 等编译工具

---

## 📦 步骤 1：安装 Termux 依赖

在 Termux 中执行：

```bash
# 更新包列表
pkg update && pkg upgrade -y

# 安装 Python 和依赖
pkg install -y python python-pip libjpeg-turbo freetype libpng libxml2 libxslt openssl

# 安装编译工具
pkg install -y clang llvm make cmake
```

---

## 📦 步骤 2：安装 Python 依赖

```bash
# 进入项目目录（根据你的实际位置调整）
cd /sdcard/loan-assistant

# 或者从项目文件复制过来
# cp -r /path/to/loan-assistant /sdcard/

# 安装 Python 依赖
pip install -r requirements.txt

# 或者手动安装
pip install requests beautifulsoup4 lxml pillow schedule aiohttp qrcode kivy
```

---

## 🚀 步骤 3：运行程序

```bash
# 直接运行
python main.py
```

---

## 📱 步骤 4：保持后台运行（可选）

### 使用 termux-wake-lock

```bash
# 安装 termux-api
pkg install termux-api

# 保持 CPU 唤醒
termux-wake-lock

# 运行程序
python main.py
```

### 使用 nohup

```bash
# 后台运行
nohup python main.py > loan-assistant.log 2>&1 &

# 查看日志
tail -f loan-assistant.log

# 停止程序
pkill -f "python main.py"
```

---

## 🔧 常见问题

### 问题 1：Kivy 安装失败

```bash
# Kivy 需要额外的依赖
pkg install -y sdl2 sdl2_image sdl2_ttf sdl2_mixer

# 然后重新安装
pip install kivy
```

### 问题 2：权限问题

```bash
# 授予存储权限（在 Android 设置中）
# 或者使用 Termux 的存储访问
termux-setup-storage
```

### 问题 3：中文显示问题

```bash
# 安装中文字体
pkg install -y fontconfig
```

---

## 📋 完整命令清单（一键执行）

```bash
# 复制以下所有命令到 Termux 执行

pkg update && pkg upgrade -y
pkg install -y python python-pip libjpeg-turbo freetype libpng libxml2 libxslt openssl clang llvm make cmake sdl2 sdl2_image sdl2_ttf sdl2_mixer
termux-setup-storage
cd /sdcard/loan-assistant
pip install -r requirements.txt
python main.py
```

---

## 📍 项目文件位置

建议将项目放在：
- `/sdcard/loan-assistant/` - 方便访问
- 或 `~/loan-assistant/` - Termux 家目录

---

## 🎯 下一步

1. **将项目文件复制到手机**
   - 通过 USB 传输
   - 或通过微信/QQ 发送到手机

2. **在 Termux 中访问项目**
   ```bash
   cd /sdcard/loan-assistant
   ```

3. **运行程序**
   ```bash
   python main.py
   ```

---

## ⚠️ 注意事项

1. **手机屏幕保持开启** - 后台任务需要屏幕常亮
2. **网络连接** - 爬虫功能需要网络
3. **电池优化** - 关闭 Termux 的电池优化
4. **存储空间** - 确保有足够空间（约 500MB）

---

**需要我帮你生成一键安装脚本吗？**
