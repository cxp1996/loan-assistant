# Windows 打包 APK - 快速指南

## 前提条件
- Windows 10/11
- 至少 10GB 可用磁盘空间
- 稳定的网络连接

## 步骤 1：安装 WSL2

### 方法一：一键安装（推荐）

1. 右键点击"开始"菜单
2. 选择 **Windows PowerShell（管理员）**
3. 输入命令：
```powershell
wsl --install
```
4. 重启电脑
5. 重启后会自动打开 Ubuntu，设置用户名和密码

### 方法二：手动安装

如果方法一失败：

1. 打开 PowerShell（管理员）
2. 执行：
```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```
3. 重启电脑
4. 在 Microsoft Store 搜索并安装 **Ubuntu 20.04**

---

## 步骤 2：在 Ubuntu 中安装依赖

打开 Ubuntu（开始菜单搜索"Ubuntu"），执行：

```bash
# 更新系统
sudo apt-get update
sudo apt-get upgrade -y

# 安装依赖
sudo apt-get install -y git zip unzip python3-pip openjdk-11-jdk wget curl cmake

# 安装 Buildozer
pip3 install buildozer cython

# 验证安装
buildozer --version
```

---

## 步骤 3：获取项目代码

```bash
# 创建项目目录
mkdir -p ~/loan-assistant
cd ~/loan-assistant

# 创建目录结构
mkdir -p config database scrapers outreach followup analytics utils
```

### 复制项目文件

项目文件位置（Windows）：
```
C:\Users\你的用户名\openclaw\workspace\loan-assistant\
```

在 Ubuntu 中复制：
```bash
# 复制所有文件（修改你的用户名）
cp -r /mnt/c/Users/Administrator/openclaw/workspace/loan-assistant/* .

# 或者手动创建核心文件
# （见下方简化方案）
```

---

## 步骤 4：配置项目

```bash
# 编辑配置文件
nano buildozer.spec
```

确保以下行正确：
```
title = 贷款客户引流助手
package.name = loanassistant
version = 1.0.0
author = Your Name
```

保存：`Ctrl+O` → 回车 → `Ctrl+X`

---

## 步骤 5：开始打包

```bash
# 在项目目录下执行
buildozer -v android debug
```

**首次运行会下载：**
- Android SDK（约 500MB）
- Android NDK（约 800MB）
- 构建工具

**耗时：30-90 分钟**

---

## 步骤 6：获取 APK

打包完成后：

```bash
# 查看 APK 文件
ls -lh bin/*.apk

# 复制到 Windows 目录
cp bin/loanassistant-1.0.0-debug.apk /mnt/c/Users/你的用户名/Downloads/
```

APK 位置（Windows）：
```
C:\Users\你的用户名\Downloads\loanassistant-1.0.0-debug.apk
```

---

## 步骤 7：安装到手机

### 方法 A：微信传输

1. 电脑登录微信
2. 发送 APK 到"文件传输助手"
3. 手机下载并安装

### 方法 B：USB 传输

1. 手机连接电脑
2. 复制 APK 到手机
3. 手机上点击安装

---

## 快速命令（复制粘贴）

```bash
# 在 Ubuntu 中依次执行：

# 1. 安装依赖
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git zip unzip python3-pip openjdk-11-jdk wget curl cmake
pip3 install buildozer cython

# 2. 创建项目
mkdir -p ~/loan-assistant && cd ~/loan-assistant
mkdir -p config database scrapers outreach followup analytics utils

# 3. 从 Windows 复制文件（修改用户名）
cp -r /mnt/c/Users/Administrator/openclaw/workspace/loan-assistant/* .

# 4. 开始打包
buildozer -v android debug

# 5. 完成后复制到 Windows
cp bin/*.apk /mnt/c/Users/Administrator/Downloads/
```

---

## 常见问题

### Q: WSL2 安装失败？
A: 确保 Windows 是最新版本，启用虚拟化功能（BIOS 设置）。

### Q: Buildozer 下载失败？
A: 使用国内镜像：
```bash
export ANDROID_HOME_MIRROR=https://mirrors.cloud.tencent.com/android
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 内存不足？
A: 在 Windows 用户目录创建 `.wslconfig` 文件：
```ini
[wsl2]
memory=4GB
swap=4GB
```

---

## 进度检查

- [ ] WSL2 已安装
- [ ] Ubuntu 已启动并设置
- [ ] 依赖已安装
- [ ] 项目代码已获取
- [ ] 打包命令已执行
- [ ] APK 已生成
- [ ] APK 已传到手机
- [ ] 应用已安装并测试

---

## 需要帮助？

遇到问题时，提供：
1. 当前执行的命令
2. 错误信息（最后 20 行）
3. Windows 版本

我会帮你解决！
