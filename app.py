#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客Flask应用主文件
完全替代Jekyll，保持原有视觉效果
"""

from flask import Flask, render_template, abort
import os
from datetime import datetime
from utils.post_manager import PostManager
from utils.markdown_parser import MarkdownParser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 配置路径
BLOG_ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BLOG_ROOT, '_posts')
PAGES_DIR = os.path.join(BLOG_ROOT, '_pages')

# 初始化组件
post_manager = PostManager(POSTS_DIR, PAGES_DIR)
markdown_parser = MarkdownParser()

# 全局模板变量
@app.context_processor
def inject_global_vars():
    return {
        'current_year': datetime.now().year
    }

@app.route('/')
def index():
    """首页 - 显示文章归档"""
    posts = post_manager.get_all_posts()
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
    all_tags = post_manager.get_all_tags()
    return render_template('tags.html', 
                         tags=all_tags, 
                         page_type='tags',
                         title='Tags')

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
    
    # 直接生成时间线视图，不使用timeline.md文件
    posts = post_manager.get_all_posts()
    print(f"Found {len(posts)} posts for timeline")
    if posts:
        print(f"First post: {posts[0].get('title', 'No title')} ({posts[0].get('date', 'No date')})")
    return render_template('timeline.html', 
                         posts=posts, 
                         page_type='timeline',
                         title='Timeline')

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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8084))
    app.run(host='0.0.0.0', port=port, debug=True)