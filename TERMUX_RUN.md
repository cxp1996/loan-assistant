# Termux 快速运行指南 - 贷款客户引流助手

## 10 分钟快速部署

### 第一步：安装 Termux（2 分钟）

**下载方式：**

1. **F-Droid（推荐，最新版本）**
   - 访问：https://f-droid.org/packages/com.termux/
   - 下载并安装

2. **GitHub（官方版本）**
   - 访问：https://github.com/termux/termux-app/releases
   - 下载最新 APK 安装

3. **应用商店**
   - 搜索 "Termux"
   - 注意：有些商店版本较旧

**⚠️ 重要：** 不要从 Google Play 下载（版本已过时）

---

### 第二步：初始化 Termux（3 分钟）

打开 Termux 应用，依次执行：

```bash
# 1. 允许存储权限（首次启动会提示，点击"允许"）

# 2. 更新包管理器
pkg update -y
pkg upgrade -y

# 3. 安装 Python
pkg install python -y

# 4. 安装依赖
pkg install wget curl nano -y
```

---

### 第三步：安装 Python 依赖（2 分钟）

```bash
# 安装项目所需依赖
pip install requests beautifulsoup4 lxml pillow schedule aiohttp qrcode

# 验证安装
python --version  # 应显示 Python 3.x
pip list | grep -E "requests|beautifulsoup4|aiohttp"
```

---

### 第四步：创建项目目录（1 分钟）

```bash
# 创建项目目录
mkdir -p /sdcard/Download/loan-assistant
cd /sdcard/Download/loan-assistant

# 授予 Termux 存储权限（如果还没授权）
termux-setup-storage
```

---

### 第五步：获取项目代码（2 分钟）

**方法 A：使用 Git（推荐）**

```bash
# 如果项目已上传到 Git
git clone <你的仓库地址> .
```

**方法 B：手动创建文件**

如果无法使用 Git，手动创建核心文件：

```bash
# 创建目录结构
mkdir -p config database scrapers outreach followup analytics utils

# 创建配置文件
nano config/settings.json
# 粘贴配置内容（见下方）
```

**方法 C：使用部署脚本**

```bash
# 下载部署脚本
wget -O deploy.sh <项目地址>/quick-deploy.sh
chmod +x deploy.sh
./deploy.sh
```

---

### 第六步：配置微信号（1 分钟）

编辑配置文件：

```bash
# 使用 nano 编辑
nano config/settings.json
```

修改以下内容：

```json
{
  "wechat_id": "你的实际微信号",
  "wechat": {
    "name": "你的名字",
    "title": "贷款顾问",
    "qr_base_path": "/sdcard/Download/wechat-qr.png"
  },
  ...
}
```

保存：按 `Ctrl+O` → 回车 → `Ctrl+X` 退出

---

### 第七步：运行程序

```bash
# 确保在项目目录
cd /sdcard/Download/loan-assistant

# 运行主程序
python main.py
```

---

## 运行模式说明

程序启动后会显示菜单：

```
==================================================
贷款客户引流助手 v1.0
==================================================

请选择运行模式:
1. 手动运行一次（抓取客户）
2. 定时任务模式（自动运行）
3. 仅生成微信二维码
4. 查看数据看板
5. 导出统计报表
6. 查看待跟进客户
7. 初始化自动回复规则
```

### 推荐操作顺序：

1. **首次运行**：选择 `7` 初始化自动回复规则
2. **测试功能**：选择 `1` 手动抓取一次
3. **查看效果**：选择 `4` 查看数据看板
4. **正式使用**：选择 `2` 开启定时任务

---

## 后台运行（保持程序持续运行）

### 方法 1：使用 tmux（推荐）

```bash
# 安装 tmux
pkg install tmux -y

# 创建新会话
tmux new -s loan

# 运行程序
python main.py
# 选择模式 2（定时任务）

# 退出但不关闭（后台运行）
# 按 Ctrl+B，然后按 D

# 重新连接会话
tmux attach -t loan

# 查看会话列表
tmux ls
```

### 方法 2：使用 nohup

```bash
# 后台运行
nohup python main.py > loan-assistant.log 2>&1 &

# 查看进程
ps aux | grep python

# 查看日志
tail -f loan-assistant.log

# 停止程序
kill $(pgrep -f "python main.py")
```

---

## 开机自启（可选）

### 使用 Termux:Boot

1. **安装 Termux:Boot 应用**
   - F-Droid 下载：https://f-droid.org/packages/com.termux.boot/

2. **创建自启脚本**
   ```bash
   mkdir -p ~/.termux/boot
   nano ~/.termux/boot/loan-assistant.sh
   ```

3. **脚本内容**
   ```bash
   #!/data/data/com.termux/files/usr/bin/bash
   cd /sdcard/Download/loan-assistant
   python main.py
   ```

4. **赋予执行权限**
   ```bash
   chmod +x ~/.termux/boot/loan-assistant.sh
   ```

5. **重启手机测试**

---

## 常见问题

### Q1: pip 安装依赖失败？

**解决方案：**
```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests beautifulsoup4 lxml pillow schedule aiohttp qrcode
```

### Q2: 运行时提示找不到模块？

**解决方案：**
```bash
# 重新安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### Q3: 抓取不到数据？

**解决方案：**
- 检查网络连接
- 部分平台可能有反爬，需要调整
- 查看日志文件了解详细错误

### Q4: 程序中断退出？

**解决方案：**
- 使用 tmux 保持后台运行
- 检查手机是否开启省电模式
- 在 Termux 设置中关闭电池优化

### Q5: 存储空间不足？

**解决方案：**
```bash
# 清理缓存
pkg clean

# 查看存储使用
df -h

# 清理旧日志
rm /sdcard/Download/loan-assistant/logs/*.log
```

---

## 数据管理

### 查看数据库

```bash
# 安装 sqlite
pkg install sqlite -y

# 查看客户数据
sqlite3 /sdcard/Download/loan-assistant/customers.db

# 执行查询
SELECT * FROM customers ORDER BY created_at DESC LIMIT 10;

# 导出 CSV
sqlite3 -header -csv customers.db "SELECT * FROM customers;" > customers.csv
```

### 查看日志

```bash
# 查看今日日志
cat /sdcard/Download/loan-assistant/logs/loan-assistant-$(date +%Y%m%d).log

# 实时查看日志
tail -f /sdcard/Download/loan-assistant/logs/loan-assistant-*.log
```

### 备份数据

```bash
# 备份数据库
cp /sdcard/Download/loan-assistant/customers.db /sdcard/Download/loan-assistant-backup-$(date +%Y%m%d).db

# 备份整个项目
tar -czf /sdcard/Download/loan-assistant-backup-$(date +%Y%m%d).tar.gz /sdcard/Download/loan-assistant/
```

---

## 性能优化

### 调整抓取频率

编辑 `config/settings.json`：

```json
{
  "scrapers": {
    "interval_minutes": 60  // 改为 60 分钟（默认 30）
  },
  "schedule": {
    "start_time": "09:00",
    "end_time": "21:00"
  }
}
```

### 限制抓取数量

```json
{
  "outreach": {
    "daily_limit": 30  // 每日最多触达 30 人
  }
}
```

---

## 快速命令参考

```bash
# 启动程序
cd /sdcard/Download/loan-assistant && python main.py

# 后台运行
tmux new -s loan -d "cd /sdcard/Download/loan-assistant && python main.py"

# 查看运行状态
tmux attach -t loan

# 停止程序
tmux kill-session -t loan

# 查看今日数据
python -c "from analytics.stats import StatisticsManager; s = StatisticsManager('/sdcard/Download/loan-assistant/customers.db'); s.print_dashboard(1)"

# 导出客户列表
sqlite3 -header -csv /sdcard/Download/loan-assistant/customers.db "SELECT username,platform,loan_type,intention_score FROM customers WHERE wechat_added=0 ORDER BY intention_score DESC LIMIT 50;" > /sdcard/Download/pending-customers.csv
```

---

## 下一步

部署完成后：

1. ✅ 运行程序测试功能
2. ✅ 查看数据看板
3. ✅ 根据实际效果调整参数
4. ✅ 开始正式使用

有任何问题随时告诉我！
