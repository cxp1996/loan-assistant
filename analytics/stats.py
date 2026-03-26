"""
数据统计与可视化模块
转化率分析、渠道效果、报表生成
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class StatisticsManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
    
    def get_daily_stats(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取每日统计数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT date, total_captured, total_outreach, total_wechat_added, conversion_rate
            FROM statistics
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC
        ''', (start_date, end_date))
        
        stats = []
        for row in cursor.fetchall():
            stats.append({
                'date': row[0],
                'total_captured': row[1],
                'total_outreach': row[2],
                'total_wechat_added': row[3],
                'conversion_rate': row[4]
            })
        
        conn.close()
        return stats
    
    def get_platform_stats(self, days: int = 30) -> List[Dict]:
        """获取各平台效果统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT 
                platform,
                COUNT(*) as total_customers,
                SUM(CASE WHEN outreach_status='contacted' THEN 1 ELSE 0 END) as contacted,
                SUM(CASE WHEN wechat_added=1 THEN 1 ELSE 0 END) as wechat_added,
                AVG(intention_score) as avg_intention_score
            FROM customers
            WHERE DATE(created_at) >= ?
            GROUP BY platform
            ORDER BY wechat_added DESC
        ''', (since_date,))
        
        stats = []
        for row in cursor.fetchall():
            conversion_rate = (row[3] / row[1] * 100) if row[1] > 0 else 0
            stats.append({
                'platform': row[0],
                'total_customers': row[1],
                'contacted': row[2],
                'wechat_added': row[3],
                'avg_intention_score': round(row[4], 1) if row[4] else 0,
                'conversion_rate': round(conversion_rate, 2)
            })
        
        conn.close()
        return stats
    
    def get_loan_type_stats(self, days: int = 30) -> List[Dict]:
        """获取贷款类型统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT 
                loan_type,
                COUNT(*) as total,
                SUM(CASE WHEN wechat_added=1 THEN 1 ELSE 0 END) as wechat_added
            FROM customers
            WHERE DATE(created_at) >= ?
            GROUP BY loan_type
        ''', (since_date,))
        
        type_map = {
            'personal': '个人消费贷',
            'business': '企业经营贷',
            'mortgage': '房贷',
            'car_loan': '车贷'
        }
        
        stats = []
        for row in cursor.fetchall():
            conversion_rate = (row[2] / row[1] * 100) if row[1] > 0 else 0
            stats.append({
                'loan_type': row[0],
                'loan_type_name': type_map.get(row[0], row[0]),
                'total': row[1],
                'wechat_added': row[2],
                'conversion_rate': round(conversion_rate, 2)
            })
        
        conn.close()
        return stats
    
    def get_funnel_stats(self, days: int = 7) -> Dict:
        """获取转化漏斗统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 获取各阶段数量
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN outreach_status!='pending' THEN 1 ELSE 0 END) as contacted,
                SUM(CASE WHEN wechat_added=1 THEN 1 ELSE 0 END) as wechat_added
            FROM customers
            WHERE DATE(created_at) >= ?
        ''', (since_date,))
        
        row = cursor.fetchone()
        
        total = row[0] or 0
        contacted = row[1] or 0
        wechat_added = row[2] or 0
        
        funnel = {
            'period_days': days,
            'stages': [
                {'name': '抓取客户', 'count': total, 'rate': 100},
                {'name': '已触达', 'count': contacted, 
                 'rate': round(contacted/total*100, 1) if total > 0 else 0},
                {'name': '已加微信', 'count': wechat_added,
                 'rate': round(wechat_added/total*100, 1) if total > 0 else 0}
            ],
            'overall_conversion': round(wechat_added/total*100, 2) if total > 0 else 0
        }
        
        conn.close()
        return funnel
    
    def get_top_customers(self, limit: int = 10, days: int = 7) -> List[Dict]:
        """获取高意向客户 TOP 榜"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT id, username, platform, loan_type, intention_score, content, created_at
            FROM customers
            WHERE DATE(created_at) >= ? AND wechat_added=0
            ORDER BY intention_score DESC, created_at ASC
            LIMIT ?
        ''', (since_date, limit))
        
        customers = []
        for row in cursor.fetchall():
            customers.append({
                'id': row[0],
                'username': row[1],
                'platform': row[2],
                'loan_type': row[3],
                'intention_score': row[4],
                'content': row[5][:100],
                'created_at': row[6]
            })
        
        conn.close()
        return customers
    
    def generate_report(self, days: int = 30, output_path: str = None) -> Dict:
        """生成综合报表"""
        report = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period_days': days,
            'summary': {},
            'platform_performance': self.get_platform_stats(days),
            'loan_type_performance': self.get_loan_type_stats(days),
            'funnel': self.get_funnel_stats(days),
            'daily_trend': self.get_daily_stats(
                (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            ),
            'top_customers': self.get_top_customers(10, days)
        }
        
        # 计算汇总数据
        daily_stats = report['daily_trend']
        if daily_stats:
            report['summary'] = {
                'total_captured': sum(s['total_captured'] for s in daily_stats),
                'total_outreach': sum(s['total_outreach'] for s in daily_stats),
                'total_wechat_added': sum(s['total_wechat_added'] for s in daily_stats),
                'avg_conversion_rate': round(
                    sum(s['conversion_rate'] for s in daily_stats) / len(daily_stats), 2
                ) if daily_stats else 0
            }
        
        # 保存到文件
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def print_dashboard(self, days: int = 7):
        """打印控制台仪表盘"""
        print("\n" + "=" * 60)
        print("📊 贷款客户引流助手 - 数据看板")
        print("=" * 60)
        
        # 汇总数据
        funnel = self.get_funnel_stats(days)
        print(f"\n📈 转化漏斗 (近{days}天)")
        print("-" * 40)
        for stage in funnel['stages']:
            bar = '█' * int(stage['rate'] / 5)
            print(f"{stage['name']:10} {stage['count']:5}人 {bar} {stage['rate']}%")
        print(f"\n整体转化率：{funnel['overall_conversion']}%")
        
        # 平台效果
        print(f"\n📱 各平台效果 (近{days}天)")
        print("-" * 40)
        platform_stats = self.get_platform_stats(days)
        for p in platform_stats[:5]:
            print(f"{p['platform']:10} 抓取:{p['total_customers']:3} 加微信:{p['wechat_added']:3} 转化:{p['conversion_rate']}%")
        
        # 贷款类型
        print(f"\n💰 贷款类型分布 (近{days}天)")
        print("-" * 40)
        loan_stats = self.get_loan_type_stats(days)
        for l in loan_stats:
            print(f"{l['loan_type_name']:12} {l['total']:3}人 加微信:{l['wechat_added']:3} 转化:{l['conversion_rate']}%")
        
        # 高意向客户
        print(f"\n🔥 高意向客户 TOP5 (待跟进)")
        print("-" * 40)
        top_customers = self.get_top_customers(5, days)
        for i, c in enumerate(top_customers, 1):
            print(f"{i}. [{c['platform']}] {c['username']} 意向度:{c['intention_score']} 类型:{c['loan_type']}")
        
        print("\n" + "=" * 60)
