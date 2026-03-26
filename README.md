# 贷款客户引流助手 - 安卓免 Root 版

## 架构设计
- **运行环境**: Termux (安卓免 root Linux 环境)
- **核心语言**: Python 3
- **数据存储**: SQLite
- **微信引流**: 活码二维码（客户主动添加）

## 目录结构
```
loan-assistant/
├── config/
│   └── settings.json      # 配置文件
├── scrapers/
│   ├── zhihu.py          # 知乎爬虫
│   ├── weibo.py          # 微博爬虫
│   ├── xianyu.py         # 闲鱼爬虫
│   └── base.py           # 爬虫基类
├── database/
│   └── db_manager.py     # 数据库管理
├── outreach/
│   └── wechat_qr.py      # 微信活码生成
├── utils/
│   ├── logger.py         # 日志工具
│   └── filters.py        # 客户筛选
├── main.py               # 主程序
├── requirements.txt      # 依赖包
└── README.md            # 使用说明
```

## 核心流程
1. 定时抓取多平台公开数据
2. 筛选有贷款需求的客户
3. 生成带追踪参数的微信活码
4. 通过平台私信/评论发送引流信息
5. 客户扫码添加微信
6. 记录转化数据
