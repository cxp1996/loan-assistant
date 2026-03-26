#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贷款客户引流助手 - Termux 手机版
功能：客户管理、微信活码、数据跟进
"""

import os
import sys
import json
import sqlite3
import time
from datetime import datetime, timedelta

# 第三方库
import requests
from bs4 import BeautifulSoup
import qrcode
from qrcode.image import svg
# 注意：移除了 PIL 依赖，使用 SVG 格式生成二维码

# ============== 配置 ==============
DB_PATH = "/sdcard/loan-assistant/customers.db"
QR_DIR = "/sdcard/loan-assistant/qrcodes"

# ============== 数据库 ==============
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            wechat TEXT,
            source TEXT,
            amount TEXT,
            status TEXT DEFAULT '新客',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            content TEXT,
            followup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

# ============== 客户管理 ==============
def add_customer():
    """添加客户"""
    print("\n" + "="*40)
    print("  添加客户")
    print("="*40)
    
    name = input("姓名：")
    phone = input("电话：")
    wechat = input("微信：")
    source = input("来源（58/百姓/抖音/其他）：")
    amount = input("需求金额：")
    notes = input("备注：")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO customers (name, phone, wechat, source, amount, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, phone, wechat, source, amount, notes))
    conn.commit()
    conn.close()
    
    print(f"\n✅ 客户 '{name}' 添加成功！")
    return True

def view_customers():
    """查看客户列表"""
    print("\n" + "="*40)
    print("  客户列表")
    print("="*40)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, phone, wechat, source, amount, status, created_at FROM customers ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("\n暂无客户数据")
        return
    
    print(f"\n{'ID':<5} {'姓名':<10} {'电话':<15} {'微信':<15} {'来源':<8} {'金额':<10} {'状态':<8} {'时间'}")
    print("-"*90)
    
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<10} {row[2]:<15} {row[3]:<15} {row[4]:<8} {row[5]:<10} {row[6]:<8} {row[7][:10]}")
    
    print(f"\n共 {len(rows)} 条记录")

def search_customer():
    """搜索客户"""
    print("\n" + "="*40)
    print("  搜索客户")
    print("="*40)
    
    keyword = input("搜索关键词（姓名/电话/微信）：")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, name, phone, wechat, source, amount, status, notes
        FROM customers
        WHERE name LIKE ? OR phone LIKE ? OR wechat LIKE ?
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print(f"\n未找到匹配 '{keyword}' 的客户")
        return
    
    print(f"\n找到 {len(rows)} 条记录：\n")
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"  姓名：{row[1]}")
        print(f"  电话：{row[2]}")
        print(f"  微信：{row[3]}")
        print(f"  来源：{row[4]}")
        print(f"  金额：{row[5]}")
        print(f"  状态：{row[6]}")
        print(f"  备注：{row[7]}")
        print("-"*40)

def update_status():
    """更新客户状态"""
    print("\n" + "="*40)
    print("  更新客户状态")
    print("="*40)
    
    customer_id = input("客户 ID：")
    print("\n状态选项：")
    print("1. 新客")
    print("2. 已联系")
    print("3. 跟进中")
    print("4. 已成交")
    print("5. 已拒绝")
    
    choice = input("\n选择状态 (1-5)：")
    status_map = {'1': '新客', '2': '已联系', '3': '跟进中', '4': '已成交', '5': '已拒绝'}
    status = status_map.get(choice, '跟进中')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE customers
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, customer_id))
    conn.commit()
    conn.close()
    
    print(f"\n✅ 客户状态已更新为 '{status}'")

# ============== 微信活码 ==============
def generate_wechat_qr():
    """生成微信活码 - 使用 SVG 格式（无需 Pillow）"""
    print("\n" + "="*40)
    print("  生成微信活码")
    print("="*40)
    
    # 确保目录存在
    os.makedirs(QR_DIR, exist_ok=True)
    
    wechat_id = input("微信号：")
    qr_name = input("活码名称（可选）：") or f"wechat_{int(time.time())}"
    
    # 创建二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"wechat:{wechat_id}")
    qr.make(fit=True)
    
    # 使用 SVG 格式保存（无需 Pillow 依赖）
    qr_path = os.path.join(QR_DIR, f"{qr_name}.svg")
    svg_img = qr.make_image(file_factory=qrcode.image.svg.SvgImage)
    svg_img.save(qr_path)
    
    print(f"\n✅ 微信活码已生成：{qr_path}")
    print(f"   微信号：{wechat_id}")
    print("\n提示：SVG 格式可以用浏览器打开，手机截图保存")

# ============== 跟进记录 ==============
def add_followup():
    """添加跟进记录"""
    print("\n" + "="*40)
    print("  添加跟进记录")
    print("="*40)
    
    customer_id = input("客户 ID：")
    content = input("跟进内容：")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO followups (customer_id, content)
        VALUES (?, ?)
    ''', (customer_id, content))
    conn.commit()
    conn.close()
    
    # 同时更新客户状态为"跟进中"
    c = conn.cursor()
    c.execute('''
        UPDATE customers SET status = '跟进中' WHERE id = ?
    ''', (customer_id,))
    conn.commit()
    conn.close()
    
    print(f"\n✅ 跟进记录已添加")

def view_followups():
    """查看跟进记录"""
    print("\n" + "="*40)
    print("  跟进记录")
    print("="*40)
    
    customer_id = input("客户 ID（留空查看全部）：")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if customer_id:
        c.execute('''
            SELECT f.id, f.customer_id, c.name, f.content, f.followup_date
            FROM followups f
            JOIN customers c ON f.customer_id = c.id
            WHERE f.customer_id = ?
            ORDER BY f.followup_date DESC
        ''', (customer_id,))
    else:
        c.execute('''
            SELECT f.id, f.customer_id, c.name, f.content, f.followup_date
            FROM followups f
            JOIN customers c ON f.customer_id = c.id
            ORDER BY f.followup_date DESC
            LIMIT 20
        ''')
    
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("\n暂无跟进记录")
        return
    
    print(f"\n{'ID':<5} {'客户 ID':<8} {'姓名':<10} {'跟进内容':<30} {'时间'}")
    print("-"*80)
    
    for row in rows:
        content = row[3][:28] + "..." if len(row[3]) > 30 else row[3]
        print(f"{row[0]:<5} {row[1]:<8} {row[2]:<10} {content:<30} {row[4][:10]}")

# ============== 数据统计 ==============
def show_stats():
    """显示统计数据"""
    print("\n" + "="*40)
    print("  数据统计")
    print("="*40)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 总数统计
    c.execute('SELECT COUNT(*) FROM customers')
    total = c.fetchone()[0]
    
    # 按状态统计
    c.execute('SELECT status, COUNT(*) FROM customers GROUP BY status')
    status_counts = c.fetchall()
    
    # 按来源统计
    c.execute('SELECT source, COUNT(*) FROM customers GROUP BY source')
    source_counts = c.fetchall()
    
    # 本月新增
    c.execute('''
        SELECT COUNT(*) FROM customers
        WHERE created_at >= date('now', 'start of month')
    ''')
    month_new = c.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 客户总数：{total}")
    print(f"📈 本月新增：{month_new}")
    
    print(f"\n按状态分布：")
    for status, count in status_counts:
        bar = "█" * count
        print(f"  {status:<10} {count:>3} {bar}")
    
    print(f"\n按来源分布：")
    for source, count in source_counts:
        bar = "█" * count
        print(f"  {source:<10} {count:>3} {bar}")

# ============== 主菜单 ==============
def show_menu():
    """显示主菜单"""
    print("\n" + "="*40)
    print("  贷款客户引流助手 - Termux 版")
    print("="*40)
    print("1. 添加客户")
    print("2. 查看客户")
    print("3. 搜索客户")
    print("4. 更新状态")
    print("5. 生成微信活码")
    print("6. 添加跟进")
    print("7. 查看跟进")
    print("8. 数据统计")
    print("0. 退出")
    print("="*40)

def main():
    """主程序"""
    print("\n🚀 贷款客户引流助手 启动中...")
    
    # 初始化数据库
    init_db()
    
    while True:
        show_menu()
        choice = input("请选择功能 (0-8)：")
        
        if choice == '1':
            add_customer()
        elif choice == '2':
            view_customers()
        elif choice == '3':
            search_customer()
        elif choice == '4':
            update_status()
        elif choice == '5':
            generate_wechat_qr()
        elif choice == '6':
            add_followup()
        elif choice == '7':
            view_followups()
        elif choice == '8':
            show_stats()
        elif choice == '0':
            print("\n👋 再见！")
            break
        else:
            print("\n❌ 无效选择，请重新输入")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序中断，再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        print("请检查错误信息或联系开发者")
        sys.exit(1)
