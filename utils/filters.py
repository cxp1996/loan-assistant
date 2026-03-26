"""
客户筛选工具
"""
import re
from typing import Dict, List

class CustomerFilter:
    def __init__(self, config: dict):
        self.config = config
        self.keywords = config.get('keywords', [])
        self.exclude_keywords = config.get('exclude_keywords', [])
    
    def filter_customers(self, customers: List[Dict]) -> List[Dict]:
        """筛选高质量客户"""
        filtered = []
        
        for customer in customers:
            # 检查意向度
            if customer.get('intention_score', 0) < 30:
                continue
            
            # 检查排除关键词
            content = customer.get('content', '').lower()
            if any(kw in content for kw in self.exclude_keywords):
                continue
            
            # 检查内容质量
            if len(content) < 10:
                continue
            
            filtered.append(customer)
        
        return filtered
    
    def prioritize_customers(self, customers: List[Dict]) -> List[Dict]:
        """对客户进行优先级排序"""
        # 按意向度降序，创建时间升序
        return sorted(
            customers,
            key=lambda x: (-x.get('intention_score', 0), x.get('created_at', ''))
        )
    
    def detect_contact_info(self, content: str) -> Dict[str, str]:
        """从内容中提取联系方式"""
        contact_info = {}
        
        # 手机号
        phone_pattern = r'1[3-9]\d{9}'
        phones = re.findall(phone_pattern, content)
        if phones:
            contact_info['phone'] = phones[0]
        
        # 微信号
        wechat_pattern = r'微信 [：:]\s*(\w+)|V[Xx][：:]\s*(\w+)|薇 [：:]\s*(\w+)'
        wechat_match = re.search(wechat_pattern, content)
        if wechat_match:
            wechat = wechat_match.group(1) or wechat_match.group(2) or wechat_match.group(3)
            contact_info['wechat'] = wechat
        
        return contact_info
