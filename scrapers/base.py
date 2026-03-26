"""
爬虫基类
定义统一的爬虫接口
"""
import aiohttp
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import json

class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.keywords = config.get('keywords', [])
        self.exclude_keywords = config.get('exclude_keywords', [])
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def calculate_intention_score(self, content: str) -> int:
        """计算客户意向度分数 (0-100)"""
        score = 0
        content_lower = content.lower()
        
        # 高意向关键词
        high_intent = ['急需', '急用', '马上', '今天', '现在', '在线等']
        for word in high_intent:
            if word in content_lower:
                score += 30
        
        # 中意向关键词
        mid_intent = ['贷款', '借款', '借钱', '融资', '贷款产品', '利息']
        for word in mid_intent:
            if word in content_lower:
                score += 15
        
        # 低意向关键词
        low_intent = ['了解', '咨询', '问问', '怎么样', '哪个好']
        for word in low_intent:
            if word in content_lower:
                score += 5
        
        # 金额信息加分
        if any(word in content_lower for word in ['万', '千', '额度', '多少']):
            score += 10
        
        # 贷款类型明确加分
        if any(word in content_lower for word in ['房贷', '车贷', '经营贷', '企业贷']):
            score += 15
        
        return min(score, 100)
    
    def detect_loan_type(self, content: str) -> str:
        """识别贷款类型"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['企业', '公司', '经营', '生意', '商户']):
            return 'business'
        elif any(word in content_lower for word in ['房贷', '买房', '购房']):
            return 'mortgage'
        elif any(word in content_lower for word in ['车贷', '买车', '购车']):
            return 'car_loan'
        else:
            return 'personal'
    
    def should_exclude(self, content: str) -> bool:
        """判断是否应该排除该内容"""
        content_lower = content.lower()
        return any(word in content_lower for word in self.exclude_keywords)
    
    @abstractmethod
    async def scrape(self) -> List[Dict]:
        """执行爬取，返回客户列表"""
        pass
    
    def parse_customer(self, data: dict) -> Optional[Dict]:
        """解析单个客户信息"""
        content = data.get('content', '')
        
        if self.should_exclude(content):
            return None
        
        return {
            'platform': self.__class__.__name__.replace('Scraper', '').lower(),
            'user_id': data.get('user_id'),
            'username': data.get('username'),
            'content': content,
            'loan_type': self.detect_loan_type(content),
            'intention_score': self.calculate_intention_score(content),
            'contact_info': data.get('contact_info'),
            'raw_data': data
        }
