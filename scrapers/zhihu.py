"""
知乎爬虫
抓取知乎贷款相关话题和回答
注意：仅抓取公开内容，遵守知乎 robots.txt
"""
import json
import re
from typing import List, Dict
from .base import BaseScraper

class ZhihuScraper(BaseScraper):
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = "https://www.zhihu.com/api/v4/search_v2"
        self.topics = [
            "贷款",
            "借钱",
            "资金周转",
            "个人贷款",
            "企业经营贷",
            "房贷",
            "车贷"
        ]
    
    async def scrape(self) -> List[Dict]:
        """抓取知乎贷款相关内容"""
        customers = []
        
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        for topic in self.topics:
            try:
                # 搜索最新内容
                params = {
                    'gk_version': 'gz-gaokao',
                    't': 'general',
                    'q': topic,
                    'correction': 1,
                    'offset': 0,
                    'limit': 20,
                    'filter_fields': '',
                    'lc_idx': 0,
                    'show_all_topics': 0,
                    'search_source': 'Filter',
                    'time_interval': 'week'  # 只抓取一周内的内容
                }
                
                async with self.session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self.parse_search_results(data, topic)
                        customers.extend(results)
                    else:
                        print(f"知乎搜索失败：{topic}, 状态码：{response.status}")
            
            except Exception as e:
                print(f"知乎爬取异常 {topic}: {str(e)}")
        
        return customers
    
    def parse_search_results(self, data: dict, topic: str) -> List[Dict]:
        """解析搜索结果"""
        customers = []
        
        if 'data' not in data:
            return customers
        
        for item in data.get('data', []):
            if item.get('type') != 'search_result':
                continue
            
            object_data = item.get('object', {})
            content = ''
            
            # 提取内容
            if 'excerpt' in object_data:
                content = self.strip_html(object_data['excerpt'])
            elif 'content' in object_data:
                content = self.strip_html(object_data['content'])
            
            if not content:
                continue
            
            # 提取用户信息
            author = object_data.get('author', {})
            if isinstance(author, dict):
                username = author.get('name', '匿名用户')
                user_id = author.get('id', 'unknown')
            else:
                username = '匿名用户'
                user_id = 'unknown'
            
            customer_data = {
                'user_id': user_id,
                'username': username,
                'content': content,
                'contact_info': None
            }
            
            parsed = self.parse_customer(customer_data)
            if parsed and parsed['intention_score'] >= 30:  # 只保留意向度>=30 的
                customers.append(parsed)
        
        return customers
    
    def strip_html(self, html: str) -> str:
        """去除 HTML 标签"""
        if not html:
            return ''
        # 去除 HTML 标签
        text = re.sub(r'<[^>]+>', '', html)
        # 去除转义字符
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        # 去除多余空白
        text = ' '.join(text.split())
        return text[:500]  # 限制长度
