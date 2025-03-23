import os

class Config:
    # 飞书应用配置
    FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID')
    FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET')
    
    # 多维表格配置
    BASE_ID = os.environ.get('BASE_ID')
    TABLE_ID = os.environ.get('TABLE_ID')
    
    # 验证环境变量
    if not all([FEISHU_APP_ID, FEISHU_APP_SECRET, BASE_ID, TABLE_ID]):
        raise ValueError("缺少必要的飞书应用配置或多维表格配置")
    
    # Flask配置
    SECRET_KEY = os.urandom(24)
    DEBUG = True
    
    # 缓存配置
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300