"""
微信活码生成模块
生成可追踪来源的微信二维码
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime
from typing import Optional

class WeChatQRGenerator:
    def __init__(self, wechat_id: str, config: dict):
        self.wechat_id = wechat_id
        self.config = config
        self.qr_base_path = Path(config.get('qr_base_path', '/sdcard/Download/wechat-qr.png'))
    
    def generate_qr(self, source: str = 'default') -> str:
        """
        生成微信二维码
        source: 来源标识，用于追踪客户来自哪个平台
        返回：二维码图片路径
        """
        # 创建输出目录
        self.qr_base_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 生成带来源信息的微信 ID
        # 注意：微信本身不支持动态码，这里生成固定二维码
        # 如需追踪来源，需要在触达时记录
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # 二维码内容（微信号）
        qr_data = f"微信号：{self.wechat_id}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # 创建二维码图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 添加文字说明
        img_with_text = self.add_text_overlay(img)
        
        # 保存图片
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"wechat-qr-{source}-{timestamp}.png"
        save_path = self.qr_base_path.parent / filename
        
        img_with_text.save(save_path)
        
        return str(save_path)
    
    def add_text_overlay(self, qr_image: Image.Image) -> Image.Image:
        """在二维码下方添加说明文字"""
        # 创建新图片（二维码 + 文字区域）
        qr_width, qr_height = qr_image.size
        text_height = 150
        new_height = qr_height + text_height
        
        new_img = Image.new('RGB', (qr_width, new_height), 'white')
        new_img.paste(qr_image, (0, 0))
        
        # 绘制文字
        draw = ImageDraw.Draw(new_img)
        
        # 尝试使用系统字体（安卓路径）
        font_paths = [
            '/system/fonts/DroidSansFallback.ttf',
            '/system/fonts/Roboto.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
        
        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 24)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # 绘制文字
        text1 = f"微信：{self.wechat_id}"
        text2 = "专业贷款顾问 | 低息快速放款"
        text3 = "个人消费贷 · 企业经营贷"
        
        # 计算文字位置（居中）
        bbox1 = draw.textbbox((0, 0), text1, font=font)
        bbox2 = draw.textbbox((0, 0), text2, font=font)
        bbox3 = draw.textbbox((0, 0), text3, font=font)
        
        text_width1 = bbox1[2] - bbox1[0]
        text_width2 = bbox2[2] - bbox2[0]
        text_width3 = bbox3[2] - bbox3[0]
        
        x1 = (qr_width - text_width1) // 2
        x2 = (qr_width - text_width2) // 2
        x3 = (qr_width - text_width3) // 2
        
        y_start = qr_height + 15
        
        draw.text((x1, y_start), text1, fill='black', font=font)
        draw.text((x2, y_start + 35), text2, fill='black', font=font)
        draw.text((x3, y_start + 70), text3, fill='black', font=font)
        
        return new_img
    
    def get_qr_message(self, platform: str = '') -> str:
        """
        获取引流话术
        platform: 平台名称，用于个性化话术
        """
        templates = {
            'zhihu': f"您好，看到您在知乎关注贷款相关信息。我是专业贷款顾问，专注个人消费贷和企业经营贷，可匹配低息产品。如需咨询请加微信：{self.wechat_id}",
            'weibo': f"您好，看到您在微博关注贷款信息。我是专业贷款顾问，可帮您对接多家机构，利率透明放款快。微信：{self.wechat_id}",
            'xianyu': f"您好，看到您在闲鱼有资金需求。我是专业贷款顾问，提供个人消费贷和企业经营贷方案。微信咨询：{self.wechat_id}",
            'default': f"您好，我是专业贷款顾问，专注个人消费贷和企业经营贷，利率低、放款快。如需咨询请加微信：{self.wechat_id}"
        }
        
        return templates.get(platform, templates['default'])
