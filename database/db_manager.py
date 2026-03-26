"""
数据库管理模块
负责客户信息的存储、查询和更新
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class CustomerDB:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 客户信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                user_id TEXT,
                username TEXT,
                content TEXT,
                loan_type TEXT,
                intention_score INTEGER DEFAULT 0,
                contact_info TEXT,
                outreach_status TEXT DEFAULT 'pending',
                wechat_added INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, user_id)
            )
        ''')
        
        # 触达记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                method TEXT,
                content TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # 统计数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                total_captured INTEGER DEFAULT 0,
                total_outreach INTEGER DEFAULT 0,
                total_wechat_added INTEGER DEFAULT 0,
                conversion_rate REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_customer(self, customer_data: dict) -> int:
        """添加或更新客户信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO customers 
                (platform, user_id, username, content, loan_type, intention_score, contact_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, user_id) DO UPDATE SET
                    content = excluded.content,
                    intention_score = excluded.intention_score,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                customer_data.get('platform'),
                customer_data.get('user_id'),
                customer_data.get('username'),
                customer_data.get('content'),
                customer_data.get('loan_type'),
                customer_data.get('intention_score', 0),
                customer_data.get('contact_info')
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return 0
        finally:
            conn.close()
    
    def get_pending_customers(self, limit: int = 50) -> list:
        """获取待触达的客户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, platform, username, content, loan_type, intention_score
            FROM customers
            WHERE outreach_status = 'pending'
            ORDER BY intention_score DESC, created_at ASC
            LIMIT ?
        ''', (limit,))
        
        customers = []
        for row in cursor.fetchall():
            customers.append({
                'id': row[0],
                'platform': row[1],
                'username': row[2],
                'content': row[3],
                'loan_type': row[4],
                'intention_score': row[5]
            })
        
        conn.close()
        return customers
    
    def update_outreach_status(self, customer_id: int, status: str):
        """更新客户触达状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE customers 
            SET outreach_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, customer_id))
        
        conn.commit()
        conn.close()
    
    def mark_wechat_added(self, customer_id: int):
        """标记客户已添加微信"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE customers 
            SET wechat_added = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (customer_id,))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self, date: str = None) -> dict:
        """获取统计数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM statistics WHERE date = ?
        ''', (date,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'date': row[1],
                'total_captured': row[2],
                'total_outreach': row[3],
                'total_wechat_added': row[4],
                'conversion_rate': row[5]
            }
        return None
    
    def update_statistics(self, stats: dict):
        """更新统计数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO statistics 
            (date, total_captured, total_outreach, total_wechat_added, conversion_rate)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                total_captured = excluded.total_captured,
                total_outreach = excluded.total_outreach,
                total_wechat_added = excluded.total_wechat_added,
                conversion_rate = excluded.conversion_rate
        ''', (
            stats['date'],
            stats['total_captured'],
            stats['total_outreach'],
            stats['total_wechat_added'],
            stats['conversion_rate']
        ))
        
        conn.commit()
        conn.close()
    
    def close(self):
        """关闭数据库连接"""
        pass  # SQLite 自动管理
