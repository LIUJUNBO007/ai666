import os

class Config:
    # 飞书应用配置
    FEISHU_APP_ID = "cli_a75472bbb83a500d"
    FEISHU_APP_SECRET = "YoCfSgSr6pHgeRQqV6skJcuwwhOlmf4n"
    
    # 多维表格配置
    BASE_ID = "D0olbfeHEaDMPqsz3f2c17adnyd"
    TABLE_ID = "tblBzpqhO3ODWOE7"
    
    # Flask配置
    SECRET_KEY = os.urandom(24)
    DEBUG = True
    
    # 缓存配置
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300