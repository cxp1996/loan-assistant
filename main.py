#!/usr/bin/env python3
"""
贷款客户引流助手 - 主程序
运行在安卓 Termux 环境
"""
import asyncio
import json
import schedule
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 导入模块
from database.db_manager import CustomerDB
from scrapers.zhihu import ZhihuScraper
from scrapers.weibo import WeiboScraper
from scrapers.xianyu import XianyuScraper
from outreach.wechat_qr import WeChatQRGenerator
from followup.manager import FollowUpManager
from analytics.stats import StatisticsManager
from utils.logger import setup_logger
from utils.filters import CustomerFilter

class LoanAssistant:
    def __init__(self, config_path: str = 'config/settings.json'):
        # 加载配置
        self.config = self.load_config(config_path)
        
        # 初始化日志
        self.logger = setup_logger()
        self.logger.info("贷款客户引流助手启动中...")
        
        # 初始化数据库
        db_path = self.config['database']['path']
        self.db = CustomerDB(db_path)
        self.logger.info(f"数据库初始化完成：{db_path}")
        
        # 初始化微信活码生成器
        wechat_id = input("请输入您的微信号：") if not self.config.get('wechat_id') else self.config['wechat_id']
        self.qr_generator = WeChatQRGenerator(wechat_id, self.config['wechat'])
        self.logger.info(f"微信活码生成器初始化完成")
        
        # 初始化筛选器
        self.filter = CustomerFilter(self.config['scrapers'])
        
        # 初始化跟进管理器
        self.followup = FollowUpManager(db_path, self.config.get('followup', {}))
        self.logger.info("客户跟进管理器初始化完成")
        
        # 初始化统计管理器
        self.stats_manager = StatisticsManager(db_path)
        self.logger.info("数据统计管理器初始化完成")
        
        # 统计数据
        self.stats = {
            'total_captured': 0,
            'total_outreach': 0,
            'total_wechat_added': 0
        }
    
    def load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在：{config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def scrape_all(self) -> List[Dict]:
        """执行所有爬虫"""
        all_customers = []
        
        scrapers_config = self.config['scrapers']
        enabled_scrapers = scrapers_config.get('enabled', [])
        
        self.logger.info(f"开始抓取数据，启用平台：{enabled_scrapers}")
        
        # 知乎爬虫
        if 'zhihu' in enabled_scrapers:
            try:
                async with ZhihuScraper(scrapers_config) as scraper:
                    customers = await scraper.scrape()
                    all_customers.extend(customers)
                    self.logger.info(f"知乎抓取完成：{len(customers)} 条")
            except Exception as e:
                self.logger.error(f"知乎爬取失败：{str(e)}")
        
        # 微博爬虫
        if 'weibo' in enabled_scrapers:
            try:
                async with WeiboScraper(scrapers_config) as scraper:
                    customers = await scraper.scrape()
                    all_customers.extend(customers)
                    self.logger.info(f"微博抓取完成：{len(customers)} 条")
            except Exception as e:
                self.logger.error(f"微博爬取失败：{str(e)}")
        
        return all_customers
    
    def process_customers(self, customers: List[Dict]):
        """处理抓取的客户数据"""
        # 筛选高质量客户
        filtered = self.filter.filter_customers(customers)
        self.logger.info(f"筛选后客户数：{len(filtered)}")
        
        # 保存到数据库
        for customer in filtered:
            customer_id = self.db.add_customer(customer)
            if customer_id:
                self.stats['total_captured'] += 1
                self.logger.debug(f"客户入库：{customer.get('username')} (ID: {customer_id})")
        
        return filtered
    
    def generate_outreach_materials(self):
        """生成触达素材"""
        # 生成微信二维码
        qr_path = self.qr_generator.generate_qr('general')
        self.logger.info(f"微信二维码已生成：{qr_path}")
        
        # 输出引流话术
        platforms = ['zhihu', 'weibo', 'xianyu', 'default']
        for platform in platforms:
            message = self.qr_generator.get_qr_message(platform)
            self.logger.info(f"[{platform}] 引流话术：{message}")
    
    async def run_once(self):
        """执行一次完整流程"""
        self.logger.info("=" * 50)
        self.logger.info(f"开始执行任务：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 抓取数据
        customers = await self.scrape_all()
        
        # 2. 处理客户数据
        self.process_customers(customers)
        
        # 3. 生成触达素材
        self.generate_outreach_materials()
        
        # 4. 获取待触达客户（用于后续手动或自动触达）
        pending_customers = self.db.get_pending_customers(limit=50)
        self.logger.info(f"待触达客户数：{len(pending_customers)}")
        
        # 5. 输出触达建议
        if pending_customers:
            self.logger.info("\n--- 待触达客户列表 (前 10 个) ---")
            for i, customer in enumerate(pending_customers[:10], 1):
                self.logger.info(
                    f"{i}. [{customer['platform']}] {customer['username']} | "
                    f"意向度：{customer['intention_score']} | 类型：{customer['loan_type']}"
                )
                self.logger.info(f"   内容：{customer['content'][:100]}...")
        
        # 6. 更新统计
        self.update_statistics()
        
        self.logger.info(f"任务执行完成")
        self.logger.info("=" * 50)
    
    def update_statistics(self):
        """更新统计数据"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        stats = {
            'date': today,
            'total_captured': self.stats['total_captured'],
            'total_outreach': self.stats['total_outreach'],
            'total_wechat_added': self.stats['total_wechat_added'],
            'conversion_rate': 0
        }
        
        if stats['total_outreach'] > 0:
            stats['conversion_rate'] = stats['total_wechat_added'] / stats['total_outreach'] * 100
        
        self.db.update_statistics(stats)
    
    def run_scheduled(self):
        """运行定时任务"""
        schedule_config = self.config['schedule']
        
        # 设置定时任务
        if schedule_config.get('enabled', True):
            interval = self.config['scrapers'].get('interval_minutes', 30)
            schedule.every(interval).minutes.do(asyncio.run, self.run_once())
            
            self.logger.info(f"定时任务已启动，间隔：{interval}分钟")
            
            # 运行在指定时间段内
            start_time = schedule_config.get('start_time', '09:00')
            end_time = schedule_config.get('end_time', '21:00')
            
            self.logger.info(f"运行时段：{start_time} - {end_time}")
            
            # 主循环
            while True:
                schedule.run_pending()
                time.sleep(60)
    
    def run_manual(self):
        """手动运行一次"""
        asyncio.run(self.run_once())
    
    def show_dashboard(self, days: int = 7):
        """显示数据看板"""
        self.stats_manager.print_dashboard(days)
    
    def export_report(self, days: int = 30):
        """导出统计报表"""
        output_path = f"/sdcard/Download/loan-assistant/report-{datetime.now().strftime('%Y%m%d')}.json"
        report = self.stats_manager.generate_report(days, output_path)
        self.logger.info(f"报表已导出：{output_path}")
        return report
    
    def process_followups(self):
        """处理待执行的跟进任务"""
        pending = self.followup.get_pending_followups()
        
        if pending:
            self.logger.info(f"\n待执行跟进任务：{len(pending)}个")
            for task in pending[:10]:
                self.logger.info(f"- [{task['followup_type']}] {task['username']}: {task['content'][:50]}...")
        else:
            self.logger.info("\n暂无待执行跟进任务")
        
        return pending
    
    def close(self):
        """关闭资源"""
        self.db.close()
        self.logger.info("程序已退出")


def main():
    """主函数"""
    print("=" * 50)
    print("贷款客户引流助手 v1.0")
    print("运行环境：安卓 Termux")
    print("=" * 50)
    print()
    
    # 初始化
    assistant = LoanAssistant()
    
    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 手动运行一次（抓取客户）")
    print("2. 定时任务模式（自动运行）")
    print("3. 仅生成微信二维码")
    print("4. 查看数据看板")
    print("5. 导出统计报表")
    print("6. 查看待跟进客户")
    print("7. 初始化自动回复规则")
    
    choice = input("\n请输入选项 (1-7): ").strip()
    
    try:
        if choice == '1':
            assistant.run_manual()
        elif choice == '2':
            assistant.run_scheduled()
        elif choice == '3':
            assistant.generate_outreach_materials()
        elif choice == '4':
            days = int(input("查看最近几天的数据 (默认 7): ") or "7")
            assistant.show_dashboard(days)
        elif choice == '5':
            days = int(input("导出最近几天的报表 (默认 30): ") or "30")
            assistant.export_report(days)
        elif choice == '6':
            assistant.process_followups()
        elif choice == '7':
            # 初始化默认自动回复规则
            assistant.followup.add_auto_reply_rule("利息", "您好，我们的贷款利率根据资质而定，一般年化 3.5%-18%。具体需要根据您的情况评估，可以详细说说您的需求吗？")
            assistant.followup.add_auto_reply_rule("额度", "您好，贷款额度根据您的资质而定，个人消费贷最高 50 万，企业经营贷最高 500 万。请问您需要的金额大概是多少？")
            assistant.followup.add_auto_reply_rule("条件", "您好，个人贷款需要：1) 年满 22 周岁 2) 有稳定收入 3) 征信良好。企业贷款需要：1) 营业执照满 1 年 2) 有流水。请问您符合哪些条件？")
            assistant.followup.add_auto_reply_rule("材料", "您好，需要准备：1) 身份证 2) 银行卡流水 3) 工作证明/营业执照。有房产/车产可以提高额度。您现在方便准备哪些材料？")
            print("✅ 已初始化自动回复规则")
        else:
            print("无效选项")
    except KeyboardInterrupt:
        print("\n程序中断")
    finally:
        assistant.close()


if __name__ == '__main__':
    main()
