"""
日志工具模块
"""
import logging
from pathlib import Path
from datetime import datetime

def setup_logger(log_path: str = '/sdcard/Download/loan-assistant/logs') -> logging.Logger:
    """配置日志系统"""
    
    # 创建日志目录
    log_dir = Path(log_path)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建 logger
    logger = logging.getLogger('loan_assistant')
    logger.setLevel(logging.INFO)
    
    # 清除已有 handlers
    logger.handlers.clear()
    
    # 文件 handler
    date_str = datetime.now().strftime('%Y%m%d')
    file_handler = logging.FileHandler(
        log_dir / f'loan-assistant-{date_str}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
