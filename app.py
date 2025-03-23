from flask import Flask, render_template, request, redirect, url_for, abort
import requests
import json
from config import Config
from flask_caching import Cache

app = Flask(__name__)
app.config.from_object(Config)

# 初始化缓存
cache = Cache(app)

# 飞书API基础URL
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis/"

# 获取飞书访问令牌
@cache.cached(timeout=7000, key_prefix='feishu_token')
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "app_id": app.config['FEISHU_APP_ID'],
        "app_secret": app.config['FEISHU_APP_SECRET']
    }
    
    try:
        app.logger.info(f"正在获取飞书访问令牌，使用APP_ID: {app.config['FEISHU_APP_ID']}")
        response = requests.post(url, headers=headers, json=data)
        app.logger.info(f"飞书访问令牌API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            app.logger.info(f"飞书访问令牌API响应内容: {result}")
            if result.get("code") == 0:
                app.logger.info("成功获取飞书访问令牌")
                return result.get("tenant_access_token")
            else:
                app.logger.error(f"获取飞书访问令牌失败，错误码: {result.get('code')}，错误信息: {result.get('msg')}")
        else:
            app.logger.error(f"获取飞书访问令牌请求失败，状态码: {response.status_code}")
    except Exception as e:
        app.logger.error(f"获取飞书访问令牌异常: {str(e)}")
    
    return None

# 从飞书多维表格获取数据
@cache.cached(timeout=300, key_prefix='feishu_articles')
def get_articles():
    token = get_feishu_token()
    if not token:
        app.logger.error("无法获取飞书访问令牌，无法继续获取多维表格数据")
        return []
    
    app.logger.info(f"正在获取多维表格数据，BASE_ID: {app.config['BASE_ID']}, TABLE_ID: {app.config['TABLE_ID']}")
    url = f"{FEISHU_BASE_URL}bitable/v1/apps/{app.config['BASE_ID']}/tables/{app.config['TABLE_ID']}/records"
    # url = f"{FEISHU_BASE_URL}bitable/v1/apps/D0olbfeHEaDMPqsz3f2c17adnyd/tables/tblBzpqhO3ODWOE7/records"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        app.logger.info(f"发送请求到飞书多维表格API: {url}")
        response = requests.get(url, headers=headers)
        app.logger.info(f"飞书多维表格API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            app.logger.info(f"飞书多维表格API响应内容: {result}")
            
            if result.get("code") == 0:
                items = result.get("data", {}).get("items", [])
                app.logger.info(f"获取到 {len(items)} 条记录")
                articles = []
                
                for item in items:
                    fields = item.get("fields", {})
                    app.logger.info(f"处理记录: {item.get('record_id')}, 字段: {fields}")
                    article = {
                        "id": item.get("record_id"),
                        "title": fields.get("标题", ""),
                        "quote": fields.get("金句输出", ""),
                        "comment": fields.get("黄叔点评", ""),
                        "content": fields.get("概要内容输出", ""),
                        "created_time": fields.get("创建时间", "")
                    }
                    articles.append(article)
                
                app.logger.info(f"成功处理 {len(articles)} 篇文章")
                return articles
            else:
                app.logger.error(f"获取飞书多维表格数据失败，错误码: {result.get('code')}，错误信息: {result.get('msg')}")
        else:
            app.logger.error(f"获取飞书多维表格数据请求失败，状态码: {response.status_code}，响应: {response.text}")
    except Exception as e:
        app.logger.error(f"获取飞书多维表格数据异常: {str(e)}")
    
    return []

# 获取单篇文章
def get_article(article_id):
    articles = get_articles()
    for article in articles:
        if article["id"] == article_id:
            return article
    return None

# 首页路由
@app.route('/')
def index():
    articles = get_articles()
    from datetime import datetime
    now = datetime.now()
    return render_template('index.html', articles=articles, now=now)

# 文章详情页路由
@app.route('/article/<article_id>')
def article_detail(article_id):
    article = get_article(article_id)
    if not article:
        abort(404)
    from datetime import datetime
    now = datetime.now()
    return render_template('detail.html', article=article, now=now)

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    from datetime import datetime
    now = datetime.now()
    return render_template('404.html', now=now), 404

@app.errorhandler(500)
def server_error(e):
    from datetime import datetime
    now = datetime.now()
    return render_template('500.html', now=now), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)