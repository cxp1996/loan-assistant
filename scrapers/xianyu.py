"""
58 同城爬虫
抓取 58 同城商务服务、资金需求相关帖子
注意：仅抓取公开内容
"""
import json
import re
from typing import List, Dict
from scrapers.base import BaseScraper

class XianyuScraper(BaseScraper):
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = "https://api.goofish.com/gateway/api"
        self.keywords = [
            "资金周转",
            "借钱",
            "贷款",
            "借款",
            "融资",
            "生意周转"
        ]
    
    async def scrape(self) -> List[Dict]:
        """抓取闲鱼贷款相关内容"""
        customers = []
        
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        for keyword in self.keywords:
            try:
                params = {
                    'q': keyword,
                    'page': 1,
                    'pageSize': 20,
                    'sort': 'default'
                }
                
                async with self.session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self.parse_results(data, keyword)
                        customers.extend(results)
                    else:
                        print(f"闲鱼搜索失败：{keyword}, 状态码：{response.status}")
            
            except Exception as e:
                print(f"闲鱼爬取异常 {keyword}: {str(e)}")
        
        return customers
    
    def parse_results(self, data: dict, keyword: str) -> List[Dict]:
        """解析搜索结果"""
        customers = []
        
        items = data.get('data', {}).get('items', [])
        
        for item in items:
            content = item.get('title', '') + ' ' + item.get('content', '')
            
            if not content:
                continue
            
            # 提取用户信息
            user = item.get('user', {})
            username = user.get('nickname', '未知用户')
            user_id = str(user.get('id', 'unknown'))
            
            customer_data = {
                'user_id': user_id,
                'username': username,
                'content': content[:500],
                'contact_info': None
            }
            
            parsed = self.parse_customer(customer_data)
            if parsed and parsed['intention_score'] >= 30:
                customers.append(parsed)
        
        return customers
