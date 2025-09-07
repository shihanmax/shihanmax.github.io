#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客Flask应用主文件
完全替代Jekyll，保持原有视觉效果
"""

from flask import Flask, render_template, abort, request, jsonify, session, redirect, url_for
import os
from datetime import datetime
from functools import wraps
from utils.post_manager import PostManager
from utils.markdown_parser import MarkdownParser
from utils.bookmark_manager import BookmarkManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Gs67Gty3fged672'

# 管理员认证配置
ADMIN_USERNAME = 'max'  # 可以修改为您的用户名
ADMIN_PASSWORD = 'sh123max'  # 请修改为您的密码


# 认证装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': '需要管理员权限'}), 401
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
                         title=post['title'])

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
def api_add_bookmark():
    """添加新书签 - 需要管理员权限"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data or not data.get('title') or not data.get('url'):
            return jsonify({
                'success': False,
                'error': '标题和网址为必填项'
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
def admin_login():
    """管理员登录"""
    if request.method == 'GET':
        # 如果已经登录，重定向到书签页面
        if session.get('admin_logged_in'):
            return redirect(url_for('bookmarks'))
        return render_template('admin_login.html')
    
    elif request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return jsonify({
                'success': True,
                'message': '登录成功'
            })
        else:
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

@app.route('/api/posts/<int:year>/<int:month>/<slug>/save', methods=['POST'])
@admin_required
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
def preview_post(year, month, slug):
    """预览文章内容 - 需要管理员权限"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        # 渲染内容
        rendered_content = markdown_parser.render(content)
        
        return jsonify({
            'success': True,
            'html': rendered_content
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=True)