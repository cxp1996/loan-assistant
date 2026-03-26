# 贷款客户引流助手 - 安卓安装指南

## 系统要求
- 安卓 7.0 及以上版本
- 存储空间：至少 500MB
- 网络连接：WiFi 或移动数据

## 安装步骤

### 第一步：安装 Termux

1. **下载 Termux**
   - 推荐从 F-Droid 下载（最新版本）
   - 下载地址：https://f-droid.org/packages/com.termux/
   - 或在应用商店搜索 "Termux"

2. **安装后首次启动**
   ```bash
   # 更新包管理器
   pkg update && pkg upgrade -y
   
   # 授予存储权限（在安卓设置中）
   # 设置 → 应用 → Termux → 权限 → 存储 → 允许
   ```

### 第二步：安装 Python 环境

```bash
# 安装 Python
pkg install python -y

# 安装 Python 依赖
pip install requests beautifulsoup4 lxml pillow schedule aiohttp qrcode

# 验证安装
python --version  # 应显示 Python 3.x
```

### 第三步：部署项目

```bash
# 创建项目目录
mkdir -p /sdcard/Download/loan-assistant
cd /sdcard/Download/loan-assistant

# 从你的电脑复制项目文件到手机
# 方法 1: 使用 SCP
# 方法 2: 使用 Git
git clone <你的仓库地址> .

# 或者手动创建文件（复制上方代码）
```

### 第四步：配置微信号

编辑 `config/settings.json` 文件：

```bash
# 使用 nano 编辑
nano config/settings.json

# 修改以下字段：
{
  "wechat": {
    "name": "你的名字",
    "title": "贷款顾问",
    "qr_base_path": "/sdcard/Download/wechat-qr.png"
  },
  "wechat_id": "你的实际微信号"  // 添加这一行
}
```

### 第五步：运行程序

```bash
# 进入项目目录
cd /sdcard/Download/loan-assistant

# 运行主程序
python main.py
```

### 第六步：设置开机自启（可选）

创建 Termux 自启脚本：

```bash
# 创建自启脚本
mkdir -p ~/.termux/boot
nano ~/.termux/boot/loan-assistant.sh
```

内容：
```bash
#!/data/data/com.termux/files/usr/bin/bash
cd /sdcard/Download/loan-assistant
python main.py
```

赋予执行权限：
```bash
chmod +x ~/.termux/boot/loan-assistant.sh
```

## 使用说明

### 运行模式

1. **手动模式**：运行一次抓取任务
2. **定时模式**：每 30 分钟自动抓取（可配置）
3. **仅生成二维码**：生成微信引流二维码

### 查看数据

```bash
# 查看数据库
sqlite3 /sdcard/Download/loan-assistant/customers.db

# 查看日志
cat /sdcard/Download/loan-assistant/logs/loan-assistant-20260318.log
```

### 导出客户数据

```bash
# 导出为 CSV
sqlite3 -header -csv /sdcard/Download/loan-assistant/customers.db \
  "SELECT * FROM customers WHERE wechat_added=0;" > /sdcard/Download/customers.csv
```

## 注意事项

### ⚠️ 合规提醒

1. **仅抓取公开数据**：不要爬取需要登录的内容
2. **控制触达频率**：同一客户最多联系 2 次
3. **提供退订选项**：在消息中说明"如不需要请忽略"
4. **遵守平台规则**：各平台对营销内容有限制

### ⚠️ 微信风控

1. **使用二维码让客户主动添加**（最安全）
2. 不要主动批量添加好友（有封号风险）
3. 新号前 2 周控制添加频率（每日<10 人）
4. 准备备用微信号

### ⚠️ 性能优化

1. **定时任务间隔**：建议 30-60 分钟，不要太频繁
2. **运行时段**：设置 9:00-21:00，避免夜间打扰
3. **数据清理**：定期清理 30 天前的数据

## 常见问题

### Q: 爬虫抓取不到数据？
A: 检查网络连接，部分平台可能有反爬措施，需要调整请求头或使用代理。

### Q: 二维码无法生成？
A: 确保已安装 Pillow 库：`pip install pillow`

### Q: 程序运行报错？
A: 查看日志文件，通常是依赖包缺失或配置错误。

### Q: 如何增加新的数据源？
A: 参考 `scrapers/zhihu.py` 的格式，创建新的爬虫类并继承 `BaseScraper`。

## 技术支持

如有问题，请查看日志文件或联系开发者。
