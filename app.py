#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客Flask应用主文件
完全替代Jekyll，保持原有视觉效果
"""
import logging
from flask import (Flask, render_template, abort, request, jsonify, session,
                   redirect, url_for, send_from_directory)
import os
from datetime import datetime
from functools import wraps
from utils.post_manager import PostManager
from utils.markdown_parser import MarkdownParser
from utils.bookmark_manager import BookmarkManager
from utils.security_logger import SecurityLogger
import bcrypt
from flask_wtf.csrf import CSRFProtect

# 加载.env文件中的环境变量

from dotenv import load_dotenv


logger = logging.getLogger(__name__)
# 显式指定.env文件路径
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), './deploy/.env')

# 加载.env文件，显式指定路径并启用详细输出
load_result = load_dotenv(env_path, verbose=True)

logger.info(f"load env from {env_path}, succeed: {load_result}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# 添加CSRF保护
csrf = CSRFProtect(app)

# 初始化安全日志记录器
security_logger = SecurityLogger()

# 管员认证配置
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')  # 应该存储哈希后的密码

# 简单的登录尝试次数跟踪（生产环境应使用Redis等）
login_attempts = {}


# 认证装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Permission Denied 😭'}), 401
        return f(*args, **kwargs)
    return decorated_function


# 配置路径
BLOG_ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BLOG_ROOT, '_posts')
PAGES_DIR = os.path.join(BLOG_ROOT, '_pages')

# 初始化组件
post_manager = PostManager(POSTS_DIR, PAGES_DIR)
markdown_parser = MarkdownParser()
bookmark_manager = BookmarkManager()

# 全局模板变量
@app.context_processor
def inject_global_vars():
    return {
        'current_year': datetime.now().year
    }

@app.before_request
def check_file_access():
    """检查文件访问权限，防止直接访问敏感文件"""
    # 获取客户端IP
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # 禁止直接访问敏感目录和文件
    sensitive_paths = ['/data/', '/deploy/', '/utils/', '/venv/']
    request_path = request.path
    
    for sensitive_path in sensitive_paths:
        if request_path.startswith(sensitive_path):
            # 只允许管理员访问
            if not session.get('admin_logged_in'):
                # 记录未授权访问尝试
                security_logger.log_unauthorized_access(client_ip, request_path, user_agent)
                abort(403)  # 禁止访问

@app.route('/')
def index():
    """首页 - 显示文章归档"""
    # 根据登录状态获取可见的文章
    is_logged_in = bool(session.get('admin_logged_in'))
    posts = post_manager.get_posts_by_visibility(is_logged_in)
    posts_by_year = post_manager.group_posts_by_year(posts)
    return render_template('index.html', 
                         posts_by_year=posts_by_year, 
                         page_type='home',
                         title='Home')

@app.route('/<int:year>/<int:month>/<slug>')
def post_detail(year, month, slug):
    """文章详情页"""
    post = post_manager.get_post_by_slug(year, month, slug)
    if not post:
        abort(404)
    
    # 检查文章的可见性
    display_type = post.get('display_type', 'post')
    is_logged_in = bool(session.get('admin_logged_in'))
    
    # 非登录状态下，隐藏display_type为'none'或'note'的文章
    if not is_logged_in and display_type in ['none', 'note']:
        abort(404)
    
    # 使用缓存渲染markdown内容
    post['rendered_content'] = post_manager.get_rendered_post_content(
        year, month, slug, markdown_parser
    )
    
    return render_template('post.html', 
                         post=post, 
                         page_type='post',
                         title=post['title'],
                         post_date=post['date'])

@app.route('/tags')
def tags():
    """标签页面"""
    # 根据登录状态获取可见的文章标签
    is_logged_in = bool(session.get('admin_logged_in'))
    all_tags = post_manager.get_tags_by_visibility(is_logged_in)
    return render_template('tags.html', 
                         tags=all_tags, 
                         page_type='tags',
                         title='Tags')

@app.route('/bookmarks')
def bookmarks():
    """书签页面"""
    # 获取书签页面内容
    bookmarks_content = post_manager.get_page_content('bookmarks.md')
    if bookmarks_content:
        bookmarks_content['rendered_content'] = post_manager.get_rendered_page_content(
            'bookmarks.md', markdown_parser
        )
    
    # 获取书签数据
    bookmarks_list = bookmark_manager.get_all_bookmarks()
    
    return render_template('bookmarks.html',
                         page=bookmarks_content,
                         bookmarks=bookmarks_list,
                         page_type='bookmarks',
                         title='Bookmarks')

@app.route('/about')
def about():
    """关于页面"""
    about_content = post_manager.get_page_content('about.md')
    if about_content:
        about_content['rendered_content'] = post_manager.get_rendered_page_content(
            'about.md', markdown_parser
        )
    return render_template('page.html', 
                         page=about_content, 
                         page_type='about',
                         title='About')

@app.route('/links')
def links():
    """友链页面"""
    links_content = post_manager.get_page_content('links.md')
    if links_content:
        links_content['rendered_content'] = post_manager.get_rendered_page_content(
            'links.md', markdown_parser
        )
    return render_template('page.html', 
                         page=links_content, 
                         page_type='links',
                         title='Links')

@app.route('/timeline')
def timeline():
    """时间线页面"""
    print("Timeline route called")
    
    # 根据登录状态获取可见的文章
    is_logged_in = bool(session.get('admin_logged_in'))
    posts = post_manager.get_posts_by_visibility(is_logged_in)
    print(f"Found {len(posts)} posts for timeline")
    if posts:
        print(f"First post: {posts[0].get('title', 'No title')} ({posts[0].get('date', 'No date')})")
    return render_template('timeline.html', 
                         posts=posts, 
                         page_type='timeline',
                         title='Timeline')

# API 路由 - 书签 CRUD 操作
@app.route('/api/bookmarks', methods=['GET'])
def api_get_bookmarks():
    """获取所有书签"""
    try:
        # 获取查询参数
        search = request.args.get('search')
        tag = request.args.get('tag')
        
        if search:
            bookmarks = bookmark_manager.search_bookmarks(search)
        elif tag:
            bookmarks = bookmark_manager.get_bookmarks_by_tag(tag)
        else:
            bookmarks = bookmark_manager.get_all_bookmarks()
        
        return jsonify({
            'success': True,
            'data': bookmarks
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bookmarks', methods=['POST'])
@admin_required
@csrf.exempt  # API端点 exempt CSRF 保护
def api_add_bookmark():
    """添加新书签 - 需要管理员权限"""
    try:
        data = request.get_json()
        
        # 验证数据
        is_valid, message = validate_bookmark_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # 添加书签
        bookmark = bookmark_manager.add_bookmark(
            title=data['title'],
            url=data['url'],
            description=data.get('description', ''),
            tags=data.get('tags', [])
        )
        
        # 触发同步（异步执行，不阻塞主操作）
        import threading
        sync_thread = threading.Thread(target=bookmark_manager.sync_blog)
        sync_thread.daemon = True
        sync_thread.start()
        
        return jsonify({
            'success': True,
            'data': bookmark,
            'message': '书签添加成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bookmarks/<int:bookmark_id>', methods=['PUT'])
@admin_required
@csrf.exempt  # API端点 exempt CSRF 保护
def api_update_bookmark(bookmark_id):
    """更新书签 - 需要管理员权限"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的请求数据'
            }), 400
        
        # 更新书签
        bookmark = bookmark_manager.update_bookmark(
            bookmark_id,
            **{k: v for k, v in data.items() if k in ['title', 'url', 'description', 'tags']}
        )
        
        if bookmark:
            # 触发同步（异步执行，不阻塞主操作）
            import threading
            sync_thread = threading.Thread(target=bookmark_manager.sync_blog)
            sync_thread.daemon = True
            sync_thread.start()
            
            return jsonify({
                'success': True,
                'data': bookmark,
                'message': '书签更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '书签不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bookmarks/<int:bookmark_id>', methods=['DELETE'])
@admin_required
@csrf.exempt  # API端点 exempt CSRF 保护
def api_delete_bookmark(bookmark_id):
    """删除书签 - 需要管理员权限"""
    try:
        success = bookmark_manager.delete_bookmark(bookmark_id)
        
        if success:
            # 触发同步（异步执行，不阻塞主操作）
            import threading
            sync_thread = threading.Thread(target=bookmark_manager.sync_blog)
            sync_thread.daemon = True
            sync_thread.start()
            
            return jsonify({
                'success': True,
                'message': '书签删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '书签不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bookmarks/tags', methods=['GET'])
def api_get_tags():
    """获取所有标签"""
    try:
        tags = bookmark_manager.get_all_tags()
        return jsonify({
            'success': True,
            'data': tags
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def page_not_found(e):
    """404错误页面"""
    # 读取_pages/404.md内容
    page_content = post_manager.get_page_content('404.md')
    if page_content:
        page_content['rendered_content'] = post_manager.get_rendered_page_content(
            '404.md', markdown_parser
        )
        return render_template('page.html', 
                             page=page_content, 
                             page_type='404',
                             title='404 - Page not found'), 404
    else:
        # 如果404.md不存在，回退到原有模板
        return render_template('404.html'), 404

# 管理员登录路由
@app.route('/admin/login', methods=['GET', 'POST'])
@csrf.exempt  # 登录路由 exempt CSRF 保护
def admin_login():
    """管理员登录"""
    if request.method == 'GET':
        # 如果已经登录，重定向到书签页面
        if session.get('admin_logged_in'):
            return redirect(url_for('bookmarks'))
        return render_template('admin_login.html', title='Login')
    
    elif request.method == 'POST':
        # 获取客户端IP
        client_ip = request.remote_addr
        
        # 检查登录尝试次数
        if client_ip in login_attempts and login_attempts[client_ip]['count'] >= 5:
            security_logger.log_login_attempt(
                request.get_json().get('username', 'unknown'), 
                client_ip, 
                False
            )
            return jsonify({
                'success': False,
                'error': '登录尝试次数过多，请稍后再试'
            }), 429
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的请求数据'
            }), 400
            
        username = data.get('username')
        password = data.get('password')
        
        # 验证用户名和密码
        if username == ADMIN_USERNAME and ADMIN_PASSWORD_HASH:
            try:
                # 验证哈希密码
                if bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASH.encode('utf-8')):
                    session['admin_logged_in'] = True
                    # 重置登录尝试次数
                    if client_ip in login_attempts:
                        del login_attempts[client_ip]
                    
                    # 记录成功登录
                    security_logger.log_login_attempt(username, client_ip, True)
                    
                    return jsonify({
                        'success': True,
                        'message': '登录成功'
                    })
            except ValueError as e:
                # 处理bcrypt错误，如无效的salt
                print(f"bcrypt error: {e}")
                pass  # 继续检查明文密码
                
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD_HASH:
            # 兼容明文密码（不推荐）
            session['admin_logged_in'] = True
            if client_ip in login_attempts:
                del login_attempts[client_ip]
            
            # 记录成功登录
            security_logger.log_login_attempt(username, client_ip, True)
            
            return jsonify({
                'success': True,
                'message': '登录成功'
            })
        
        # 登录失败，增加尝试次数
        if client_ip not in login_attempts:
            login_attempts[client_ip] = {'count': 1}
        else:
            login_attempts[client_ip]['count'] += 1
            
        # 记录失败登录
        security_logger.log_login_attempt(username, client_ip, False)
            
        return jsonify({
            'success': False,
            'error': '用户名或密码错误'
        }), 401

# 管理员登出路由
@app.route('/admin/logout')
def admin_logout():
    """管理员登出"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# 检查登录状态API
@app.route('/admin/status')
def admin_status():
    """检查管理员登录状态"""
    return jsonify({
        'logged_in': bool(session.get('admin_logged_in'))
    })

# Favicon 路由
@app.route('/favicon.ico')
def favicon():
    """返回 favicon 图标"""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# 编辑器路由
@app.route('/<int:year>/<int:month>/<slug>/edit')
@admin_required
def edit_post(year, month, slug):
    """文章编辑页面 - 需要管理员权限"""
    post = post_manager.get_post_by_slug(year, month, slug)
    if not post:
        abort(404)
    
    # 读取原始内容
    try:
        with open(post['filepath'], 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except Exception as e:
        abort(500)
    
    return render_template('edit_post.html', 
                         post=post, 
                         raw_content=raw_content,
                         page_type='editor',
                         title=f'Edit: {post["title"]}')

# 新的编辑器路由 - 支持从阅读页面直接跳转
@app.route('/edit/<int:year>/<int:month>/<slug>')
@admin_required
def edit_post_direct(year, month, slug):
    """直接编辑路由 - 支持锚点跳转"""
    return edit_post(year, month, slug)

@app.route('/api/posts/<int:year>/<int:month>/<slug>/save', methods=['POST'])
@admin_required
@csrf.exempt  # API端点 exempt CSRF 保护
def save_post(year, month, slug):
    """保存文章内容 - 需要管理员权限"""
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({
                'success': False,
                'error': '内容不能为空'
            }), 400
        
        # 获取文章信息
        post = post_manager.get_post_by_slug(year, month, slug)
        if not post:
            return jsonify({
                'success': False,
                'error': '文章不存在'
            }), 404
        
        # 保存文件
        success = post_manager.save_post_content(post['filepath'], content)
        
        if success:
            # 触发同步（异步执行，不阻塞主操作）
            import threading
            sync_thread = threading.Thread(target=post_manager.sync_blog)
            sync_thread.daemon = True
            sync_thread.start()
            
            return jsonify({
                'success': True,
                'message': '保存成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存失败'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/posts/<int:year>/<int:month>/<slug>/preview', methods=['POST'])
@admin_required
@csrf.exempt  # API端点 exempt CSRF 保护
def preview_post(year, month, slug):
    """预览文章内容 - 需要管理员权限"""
    try:
        print(f"Preview request received for {year}/{month}/{slug}")
        
        # 打印请求信息用于调试
        print(f"Request Content-Type: {request.content_type}")
        print(f"Request headers: {dict(request.headers)}")
        
        data = request.get_json()
        print(f"Request data: {data}")
        
        # 检查请求数据是否有效
        if not data:
            print("Invalid request data")
            return jsonify({
                'success': False,
                'error': '无效的请求数据格式'
            }), 400
            
        content = data.get('content', '')
        print(f"Content length: {len(content)}")
        
        # 渲染内容
        rendered_content = markdown_parser.render(content)
        print("Content rendered successfully")
        
        return jsonify({
            'success': True,
            'html': rendered_content
        })
    
    except Exception as e:
        print(f"Preview error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/posts/<int:year>/<int:month>/<slug>/toc', methods=['GET'])
def get_post_toc(year, month, slug):
    """获取文章目录 - 公开API"""
    try:
        # 获取文章数据
        post = post_manager.get_post_by_slug(year, month, slug)
        if not post:
            return jsonify({
                'success': False,
                'error': '文章不存在'
            }), 404
        
        # 检查文章的可见性
        display_type = post.get('display_type', 'post')
        is_logged_in = bool(session.get('admin_logged_in'))
        
        # 非登录状态下，隐藏display_type为'none'或'note'的文章
        if not is_logged_in and display_type in ['none', 'note']:
            return jsonify({
                'success': False,
                'error': '文章不存在'
            }), 404
        
        # 解析目录
        toc_data = markdown_parser.generate_toc_json(post['content'])
        toc_summary = markdown_parser.get_toc_summary(post['content'])
        
        return jsonify({
            'success': True,
            'data': {
                'toc': toc_data,
                'summary': toc_summary
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.after_request
def after_request(response):
    """添加安全头"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


def validate_bookmark_data(data):
    """验证书签数据"""
    if not data or not isinstance(data, dict):
        return False, "无效的数据格式"
    
    # 验证必需字段
    if not data.get('title') or not data.get('url'):
        return False, "标题和网址为必填项"
    
    # 验证URL格式
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// 或 https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
        r'(?::\d+)?'  # 可选端口
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(data['url']):
        return False, "网址格式不正确"
    
    # 验证标题长度
    if len(data['title']) > 200:
        return False, "标题长度不能超过200个字符"
    
    # 验证描述长度
    if data.get('description') and len(data['description']) > 1000:
        return False, "描述长度不能超过1000个字符"
    
    # 验证标签
    if data.get('tags'):
        if not isinstance(data['tags'], list):
            return False, "标签格式不正确"
        if len(data['tags']) > 10:
            return False, "标签数量不能超过10个"
        for tag in data['tags']:
            if len(tag) > 30:
                return False, "单个标签长度不能超过30个字符"
    
    return True, "验证通过"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    # 生产环境绑定到所有接口，便于访问和监控
    app.run(host='0.0.0.0', port=port, debug=True)