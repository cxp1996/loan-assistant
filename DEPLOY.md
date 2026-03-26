# 🚀 APK 打包 - 快速部署指南

## 问题说明

本地打包因网络限制持续失败（Google 服务器无法访问）。
**解决方案：使用 GitHub Actions 云端打包** - 不受网络限制，约 40 分钟完成。

---

## 3 步完成打包

### 步骤 1：创建 GitHub 仓库（1 分钟）

1. 访问 https://github.com/new
2. 仓库名：`loan-assistant`
3. 设为 **Public** 或 **Private** 均可
4. **不要** 初始化 README/.gitignore
5. 点击 **Create repository**

### 步骤 2：推送代码（1 分钟）

在项目目录执行以下命令：

```bash
cd /home/admin/openclaw/workspace/loan-assistant

# 替换为你的 GitHub 用户名
GITHUB_USER=你的用户名

# 添加远程仓库
git remote add origin https://github.com/${GITHUB_USER}/loan-assistant.git

# 重命名分支
git branch -M main

# 推送代码
git push -u origin main
```

### 步骤 3：等待构建完成（40 分钟）

1. 访问你的仓库页面：`https://github.com/你的用户名/loan-assistant`
2. 点击 **Actions** 标签页
3. 你会看到 "Build Android APK" 正在运行
4. 等待绿色对勾 ✅ 出现
5. 点击运行记录 → 底部下载 `loan-assistant-apk`

---

## 后续打包

之后每次推送代码到 `main` 分支都会自动触发构建：

```bash
# 修改代码后
git add -A
git commit -m "修改内容"
git push
```

或者手动触发：
1. Actions → Build Android APK
2. Run workflow → Run workflow

---

## APK 安装

下载 APK 后传输到手机：

**方法 1：微信/QQ 传输**
- 发送 APK 到微信/QQ
- 在手机上下载并安装

**方法 2：HTTP 下载**
```bash
# 在电脑上
cd bin
python3 -m http.server 8000

# 手机浏览器访问：http://<电脑 IP>:8000
```

**安装前确保：**
- 手机设置 → 安全 → 允许"未知来源"
- Android 版本 ≥ 7.0

---

## 需要帮助？

如果构建失败，请提供：
1. GitHub Actions 运行链接
2. 错误日志截图

---

## 技术说明

- **构建环境**: Ubuntu 22.04 + Python 3.11
- **Android API**: 28 (兼容 Android 7.0+)
- **架构**: arm64-v8a, armeabi-v7a
- **构建时间**: 首次约 40 分钟，后续增量构建更快
