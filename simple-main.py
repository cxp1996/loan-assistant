#!/usr/bin/env python3
"""
贷款客户引流助手 - 简化版
运行在安卓 Termux 环境
"""
import json
import sqlite3
import qrcode
from qrcode.image import svg
from datetime import datetime
import requests
import re
import time
# 注意：移除了 PIL 依赖，使用 SVG 格式

# ============== 配置 ==============
WECHAT_ID = ""  # 在这里填入你的微信号
DB_PATH = "/sdcard/Download/loan-assistant/customers.db"
QR_PATH = "/sdcard/Download/loan-assistant/wechat-qr.png"

# 抓取关键词
KEYWORDS = ["贷款", "借钱", "资金周转", "借款", "融资", "缺钱", "急需钱"]

# ============== 数据库 ==============
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            username TEXT,
            content TEXT,
            loan_type TEXT,
            intention_score INTEGER,
            wechat_added INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_customer(platform, username, content, loan_type, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO customers (platform, username, content, loan_type, intention_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (platform, username, content, loan_type, score))
    conn.commit()
    conn.close()
    return c.lastrowid

def get_customers(limit=20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, platform, username, content, loan_type, intention_score 
        FROM customers 
        ORDER BY intention_score DESC 
        LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

# ============== 意向度评分 ==============
def calculate_score(content):
    score = 0
    content_lower = content.lower()
    
    # 高意向
    for word in ['急需', '急用', '马上', '今天', '现在']:
        if word in content_lower:
            score += 30
    
    # 中意向
    for word in ['贷款', '借款', '借钱', '融资']:
        if word in content_lower:
            score += 15
    
    # 金额
    if any(w in content_lower for w in ['万', '千', '额度']):
        score += 10
    
    return min(score, 100)

# ============== 贷款类型识别 ==============
def detect_loan_type(content):
    content_lower = content.lower()
    if any(w in content_lower for w in ['企业', '公司', '经营', '生意']):
        return '企业经营贷'
    elif any(w in content_lower for w in ['房贷', '买房']):
        return '房贷'
    elif any(w in content_lower for w in ['车贷', '买车']):
        return '车贷'
    else:
        return '个人消费贷'

# ============== 微信二维码生成 ==============
def generate_qr():
    """生成微信二维码 - SVG 格式（无需 PIL）"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"微信号：{WECHAT_ID}")
    qr.make(fit=True)
    
    # 使用 SVG 格式保存
    svg_path = QR_PATH.replace('.png', '.svg')
    svg_img = qr.make_image(file_factory=qrcode.image.svg.SvgImage)
    svg_img.save(svg_path)
    print(f"✅ 二维码已保存：{svg_path}")
    return svg_path

# ============== 模拟抓取（示例）==============
def scrape_demo():
    """演示用 - 模拟抓取数据"""
    print("\n📥 正在抓取客户信息...")
    
    # 这里可以接入真实的 API 或爬虫
    # 下面是示例数据
    demo_data = [
        {"platform": "知乎", "username": "用户***123", "content": "急需 5 万块钱周转，有什么贷款推荐吗？"},
        {"platform": "微博", "username": "用户***456", "content": "想了解企业经营贷，利率多少？"},
        {"platform": "知乎", "username": "用户***789", "content": "买房首付不够，有靠谱的车贷吗？"},
    ]
    
    count = 0
    for item in demo_data:
        content = item['content']
        score = calculate_score(content)
        loan_type = detect_loan_type(content)
        
        if score >= 30:
            add_customer(item['platform'], item['username'], content, loan_type, score)
            count += 1
            print(f"  ✓ [{item['platform']}] {item['username']} - 意向度:{score} - 类型:{loan_type}")
    
    print(f"\n✅ 本次抓取完成，新增 {count} 个客户")
    return count

# ============== 数据看板 ==============
def show_dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("\n" + "=" * 50)
    print("📊 贷款客户引流助手 - 数据看板")
    print("=" * 50)
    
    # 总数
    c.execute("SELECT COUNT(*) FROM customers")
    total = c.fetchone()[0]
    
    # 已加微信
    c.execute("SELECT COUNT(*) FROM customers WHERE wechat_added=1")
    added = c.fetchone()[0]
    
    # 待跟进
    c.execute("SELECT COUNT(*) FROM customers WHERE wechat_added=0")
    pending = c.fetchone()[0]
    
    print(f"\n📈 客户统计")
    print(f"  总客户数：{total}")
    print(f"  已加微信：{added}")
    print(f"  待跟进：{pending}")
    
    if total > 0:
        rate = added / total * 100
        print(f"  转化率：{rate:.1f}%")
    
    # 高意向客户 TOP5
    print(f"\n🔥 高意向客户 TOP5")
    rows = get_customers(5)
    for i, row in enumerate(rows, 1):
        print(f"  {i}. [{row[1]}] {row[2]} - 意向度:{row[5]} - {row[4]}")
    
    print("\n" + "=" * 50)
    conn.close()

# ============== 引流话术 ==============
def get_outreach_message(platform, username):
    return f"您好，看到您在{platform}关注贷款信息。我是专业贷款顾问，专注个人消费贷和企业经营贷，利率低放款快。如需咨询请加微信：{WECHAT_ID}"

# ============== 主菜单 ==============
def show_menu():
    print("\n" + "=" * 50)
    print("贷款客户引流助手 v1.0 - 简化版")
    print("=" * 50)
    print("1. 抓取客户（演示）")
    print("2. 查看数据看板")
    print("3. 生成微信二维码")
    print("4. 查看客户列表")
    print("5. 导出引流话术")
    print("0. 退出")
    print("=" * 50)

def main():
    global WECHAT_ID
    
    # 初始化
    init_db()
    
    # 输入微信号
    if not WECHAT_ID:
        WECHAT_ID = input("请输入你的微信号：").strip()
        print(f"✅ 微信号已设置：{WECHAT_ID}")
    
    while True:
        show_menu()
        choice = input("请选择 (0-5): ").strip()
        
        if choice == '1':
            scrape_demo()
        elif choice == '2':
            show_dashboard()
        elif choice == '3':
            generate_qr()
        elif choice == '4':
            rows = get_customers(20)
            print(f"\n客户列表 (共{len(rows)}个):")
            for i, row in enumerate(rows, 1):
                print(f"  {i}. [{row[1]}] {row[2]} - 意向度:{row[5]} - {row[4]}")
        elif choice == '5':
            rows = get_customers(10)
            print("\n引流话术:")
            for row in rows:
                msg = get_outreach_message(row[1], row[2])
                print(f"  - {msg}")
        elif choice == '0':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项")

if __name__ == '__main__':
    main()
