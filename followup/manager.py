"""
客户跟进模块
微信添加后的自动欢迎语、标签管理、跟进提醒
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class FollowUpManager:
    def __init__(self, db_path: str, config: dict):
        self.db_path = Path(db_path)
        self.config = config
        self.init_tables()
    
    def init_tables(self):
        """初始化跟进相关表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 跟进记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS followup_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                followup_type TEXT,
                content TEXT,
                status TEXT DEFAULT 'pending',
                scheduled_time TIMESTAMP,
                completed_time TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # 客户标签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                tag_name TEXT,
                tag_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(customer_id, tag_name),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # 自动回复规则表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auto_reply_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_keyword TEXT,
                reply_content TEXT,
                priority INTEGER DEFAULT 0,
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 聊天记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                direction TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_customer_tag(self, customer_id: int, tag_name: str, tag_category: str = 'custom'):
        """给客户添加标签"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO customer_tags (customer_id, tag_name, tag_category)
                VALUES (?, ?, ?)
            ''', (customer_id, tag_name, tag_category))
            conn.commit()
        finally:
            conn.close()
    
    def remove_customer_tag(self, customer_id: int, tag_name: str):
        """移除客户标签"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM customer_tags WHERE customer_id = ? AND tag_name = ?
        ''', (customer_id, tag_name))
        
        conn.commit()
        conn.close()
    
    def get_customer_tags(self, customer_id: int) -> List[str]:
        """获取客户的所有标签"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tag_name, tag_category FROM customer_tags 
            WHERE customer_id = ?
            ORDER BY tag_category, tag_name
        ''', (customer_id,))
        
        tags = [{'name': row[0], 'category': row[1]} for row in cursor.fetchall()]
        conn.close()
        
        return tags
    
    def schedule_followup(self, customer_id: int, followup_type: str, 
                         content: str, delay_hours: int = 24, notes: str = ''):
        """安排跟进任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scheduled_time = datetime.now() + timedelta(hours=delay_hours)
        
        cursor.execute('''
            INSERT INTO followup_records 
            (customer_id, followup_type, content, scheduled_time, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_id, followup_type, content, scheduled_time, notes))
        
        conn.commit()
        conn.close()
        
        return cursor.lastrowid
    
    def get_pending_followups(self, limit: int = 50) -> List[Dict]:
        """获取待执行的跟进任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.id, f.customer_id, c.username, c.loan_type, 
                   f.followup_type, f.content, f.scheduled_time, f.notes
            FROM followup_records f
            JOIN customers c ON f.customer_id = c.id
            WHERE f.status = 'pending' 
              AND f.scheduled_time <= datetime('now')
            ORDER BY f.scheduled_time ASC
            LIMIT ?
        ''', (limit,))
        
        followups = []
        for row in cursor.fetchall():
            followups.append({
                'id': row[0],
                'customer_id': row[1],
                'username': row[2],
                'loan_type': row[3],
                'followup_type': row[4],
                'content': row[5],
                'scheduled_time': row[6],
                'notes': row[7]
            })
        
        conn.close()
        return followups
    
    def complete_followup(self, followup_id: int, notes: str = ''):
        """标记跟进任务为已完成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE followup_records 
            SET status = 'completed', completed_time = CURRENT_TIMESTAMP, notes = ?
            WHERE id = ?
        ''', (notes, followup_id))
        
        conn.commit()
        conn.close()
    
    def add_chat_record(self, customer_id: int, direction: str, content: str):
        """添加聊天记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_history (customer_id, direction, content)
            VALUES (?, ?, ?)
        ''', (customer_id, direction, content))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, customer_id: int, limit: int = 50) -> List[Dict]:
        """获取聊天记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT direction, content, timestamp FROM chat_history
            WHERE customer_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (customer_id, limit))
        
        history = [{'direction': row[0], 'content': row[1], 'timestamp': row[2]} 
                   for row in cursor.fetchall()]
        
        conn.close()
        return history
    
    def add_auto_reply_rule(self, trigger_keyword: str, reply_content: str, priority: int = 0):
        """添加自动回复规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO auto_reply_rules (trigger_keyword, reply_content, priority)
            VALUES (?, ?, ?)
        ''', (trigger_keyword, reply_content, priority))
        
        conn.commit()
        conn.close()
    
    def match_auto_reply(self, message: str) -> Optional[str]:
        """匹配自动回复"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT reply_content FROM auto_reply_rules
            WHERE enabled = 1 AND ? LIKE '%' || trigger_keyword || '%'
            ORDER BY priority DESC
            LIMIT 1
        ''', (message,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def generate_welcome_message(self, customer: Dict) -> str:
        """生成欢迎语"""
        templates = self.config.get('welcome_templates', {
            'personal': "您好！我是您的贷款顾问{名字}。看到您关注个人贷款，我这边可以帮您匹配低息产品。请问您需要的金额大概是多少？用途是什么？",
            'business': "您好！我是您的贷款顾问{名字}。看到您关注企业经营贷，我们有多家银行产品可选，利率 3.5% 起。请问您企业成立多久？月流水大概多少？",
            'mortgage': "您好！我是您的贷款顾问{名字}。关于房贷咨询，我可以帮您对比多家银行的利率和方案。请问您是首套房还是二套？",
            'car_loan': "您好！我是您的贷款顾问{名字}。车贷方面我们有多种方案，首付最低 2 成。请问您看中的是什么车型？预算多少？"
        })
        
        loan_type = customer.get('loan_type', 'personal')
        template = templates.get(loan_type, templates['personal'])
        
        return template.format(name=self.config.get('name', '小呈'))
    
    def get_followup_statistics(self, days: int = 7) -> Dict:
        """获取跟进统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 跟进任务统计
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending
            FROM followup_records
            WHERE DATE(scheduled_time) >= ?
        ''', (since_date,))
        
        row = cursor.fetchone()
        stats = {
            'period_days': days,
            'total_followups': row[0] or 0,
            'completed_followups': row[1] or 0,
            'pending_followups': row[2] or 0
        }
        
        # 标签统计
        cursor.execute('''
            SELECT tag_category, COUNT(DISTINCT customer_id) as customer_count
            FROM customer_tags
            GROUP BY tag_category
        ''')
        
        stats['tag_stats'] = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return stats
