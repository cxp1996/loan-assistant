"""
微博爬虫
抓取微博贷款相关博文和评论
注意：仅抓取公开内容
"""
import json
import re
from typing import List, Dict
from .base import BaseScraper

class WeiboScraper(BaseScraper):
    def __init__(self, config: dict):
        super().__init__(config)
        self.search_url = "https://m.weibo.cn/api/container/getIndex"
        self.keywords = [
            "贷款",
            "借钱",
            "资金周转",
            "借款",
            "缺钱",
            "贷款推荐",
            "低息贷款"
        ]
    
    async def scrape(self) -> List[Dict]:
        """抓取微博贷款相关内容"""
        customers = []
        
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        for keyword in self.keywords:
            try:
                params = {
                    'containerid': f'100103type=1&q={keyword}',
                    'page_type': 'searchall',
                    'page': 1
                }
                
                async with self.session.get(self.search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self.parse_weibo_results(data, keyword)
                        customers.extend(results)
                    else:
                        print(f"微博搜索失败：{keyword}, 状态码：{response.status}")
            
            except Exception as e:
                print(f"微博爬取异常 {keyword}: {str(e)}")
        
        return customers
    
    def parse_weibo_results(self, data: dict, keyword: str) -> List[Dict]:
        """解析微博搜索结果"""
        customers = []
        
        cards = data.get('data', {}).get('cards', [])
        
        for card in cards:
            if card.get('card_type') != 9:  # 9 表示微博内容
                continue
            
            mblog = card.get('mblog', {})
            content = mblog.get('text', '')
            
            if not content:
                continue
            
            # 去除 HTML 标签
            content = re.sub(r'<[^>]+>', '', content)
            content = ' '.join(content.split())[:500]
            
            # 提取用户信息
            user = mblog.get('user', {})
            username = user.get('screen_name', '未知用户')
            user_id = str(user.get('id', 'unknown'))
            
            customer_data = {
                'user_id': user_id,
                'username': username,
                'content': content,
                'contact_info': None
            }
            
            parsed = self.parse_customer(customer_data)
            if parsed and parsed['intention_score'] >= 30:
                customers.append(parsed)
        
        return customers
