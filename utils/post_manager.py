#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章管理器 - 处理markdown文件读取、解析、分类等功能
"""

from logging import Logger


import os
import re
import logging
import frontmatter
import subprocess
from datetime import datetime
from collections import defaultdict, OrderedDict
from typing import List, Dict, Optional, Tuple


logger: Logger = logging.getLogger(__name__)
        

class PostManager:
    
    """文章管理器"""
    
    def _is_valid_filename(self, filename: str) -> bool:
        return re.match(r'^\d{4}-\d{1,2}-\d{1,2}-', filename)
    
    def __init__(self, posts_dir: str, pages_dir: Optional[str] = None):
        self.posts_dir = posts_dir
        self.pages_dir = pages_dir or os.path.join(os.path.dirname(posts_dir), '_pages')
        self._posts_cache = None
        self._last_cache_time = None
        self._rendered_cache = {}  # 缓存渲染后的HTML内容
        self._page_cache = {}      # 缓存页面内容
    
    def _should_refresh_cache(self) -> bool:
        """检查是否需要刷新缓存"""
        if self._posts_cache is None or self._last_cache_time is None:
            return True
        
        # 检查文件夹的最后修改时间
        try:
            posts_mtime = os.path.getmtime(self.posts_dir)
            if posts_mtime > self._last_cache_time:
                # 文件发生变化，清空渲染缓存
                self._rendered_cache.clear()
                self._page_cache.clear()
                return True
            return False
        except OSError:
            return True
    
    def _parse_filename(self, filename: str) -> Optional[Tuple[int, int, int, str]]:
        """解析文件名，提取日期和slug"""
        # 匹配格式：YYYY-MM-DD-title.md
        pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})-(.+)\.md$'
        match = re.match(pattern, filename)
        
        if match:
            year, month, day, slug = match.groups()
            try:
                return int(year), int(month), int(day), slug
            except ValueError:
                print(f"Warning: Invalid date in filename {filename}")
                return None
        
        # 对于不符合日期格式的文件，尝试生成默认日期
        if filename.endswith('.md'):
            # 获取文件的修改时间作为默认日期
            try:
                filepath = os.path.join(self.posts_dir, filename)
                if os.path.exists(filepath):
                    mtime = os.path.getmtime(filepath)
                    dt = datetime.fromtimestamp(mtime)
                    slug = filename[:-3]  # 移除.md扩展名
                    print(f"Using file modification time for {filename}: {dt.year}-{dt.month:02d}-{dt.day:02d}")
                    return dt.year, dt.month, dt.day, slug
            except Exception as e:
                print(f"Warning: Could not get file time for {filename}: {e}")
        
        print(f"Warning: Could not parse filename {filename}")
        return None
    
    def _load_posts(self) -> List[Dict]:
        """Recursively load all posts from _posts directory and subdirectories"""
        posts = []
        
        if not os.path.exists(self.posts_dir):
            print(f"Posts directory does not exist: {self.posts_dir}")
            return posts
        
        # Recursively walk through all subdirectories
        markdown_files = []
        for root, dirs, files in os.walk(self.posts_dir):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)
                    markdown_files.append((filename, filepath))
        
        print(f"Found {len(markdown_files)} markdown files in {self.posts_dir} (including subdirectories)")
        
        for filename, filepath in markdown_files:
            if not filename.endswith('.md'):
                continue
            
            # Parse filename
            parsed = self._parse_filename(filename)
            if not parsed:
                print(f"Skipping file with unparseable name: {filename}")
                continue
            
            year, month, day, slug = parsed
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                # 检查display_type字段，根据旧的display字段值进行转换
                display_type = post.metadata.get('display_type')
                if display_type is None:
                    # 如果没有display_type字段，检查旧的display字段
                    old_display = post.metadata.get('display')
                    if old_display is True:
                        display_type = 'post'
                    elif old_display is False:
                        display_type = 'none'
                    else:
                        # 默认值：以日期开头的文件为post，否则为none
                        display_type = 'post' if self._is_valid_filename(filename) else 'none'
                
                # 如果display_type为none，则不展示这篇文章
                if display_type == 'none':
                    print(f"Skipping post {filename} because display_type is set to 'none'")
                    continue
                
                # 构建文章数据
                # 优先从frontmatter的date字段获取完整的时间戳（包括小时分秒）
                frontmatter_date = post.metadata.get('date')
                if isinstance(frontmatter_date, datetime):
                    date = frontmatter_date
                else:
                    # 如果没有完整的时间戳，则只使用年月日
                    date = datetime(year, month, day)
                
                post_data = {
                    'title': post.metadata.get('title', slug.replace('-', ' ').title()),
                    'date': date,
                    'slug': slug,
                    'year': year,
                    'month': month,
                    'day': day,
                    'content': post.content,
                    'tags': post.metadata.get('tags', []),
                    'categories': post.metadata.get('categories', []),
                    'description': post.metadata.get('description', ''),
                    'layout': post.metadata.get('layout', 'post'),
                    'display_type': display_type,  # 添加display_type字段到post_data
                    'collection': post.metadata.get('collection'),  # Collection name
                    'collection_order': post.metadata.get('collection_order', 0),  # Collection order
                    'filename': filename,
                    'filepath': filepath
                }
                
                # 生成URL
                post_data['url'] = f"/{year}/{month:02d}/{slug}"
                
                posts.append(post_data)
                
            except Exception as e:
                print(f"Error loading post {filename}: {e}")
                continue
        
        print(f"Successfully loaded {len(posts)} posts")
        
        # 按日期排序（最新的在前）
        posts.sort(key=lambda x: x['date'], reverse=True)
        return posts
    
    def get_all_posts(self) -> List[Dict]:
        """获取所有文章"""
        if self._should_refresh_cache():
            self._posts_cache = self._load_posts()
            self._last_cache_time = datetime.now().timestamp()
        
        return self._posts_cache or []
    
    def get_posts_by_visibility(self, is_logged_in: bool = False) -> List[Dict]:
        """根据登录状态获取可见的文章
        非登录状态下：只显示display_type为'post'的文章
        登录状态下：显示display_type为'post'和'note'的文章
        """
        all_posts = self.get_all_posts()
        
        if is_logged_in:
            # 登录状态下显示post和note类型的文章
            filtered_posts = [post for post in all_posts if post.get('display_type') in ['post', 'note']]
        else:
            # 非登录状态下只显示post类型的文章
            filtered_posts = [post for post in all_posts if post.get('display_type') == 'post']
        
        return filtered_posts
    
    def get_post_by_slug(self, year: int, month: int, slug: str) -> Optional[Dict]:
        """根据年月和slug获取文章"""
        posts = self.get_all_posts()
        
        for post in posts:
            if (post['year'] == year and 
                post['month'] == month and 
                post['slug'] == slug):
                return post
        
        return None
    
    def group_posts_by_year(self, posts: List[Dict]) -> OrderedDict:
        """按年份分组文章"""
        grouped = defaultdict(list)
        
        for post in posts:
            grouped[post['year']].append(post)
        
        # 转换为有序字典，按年份降序
        return OrderedDict(sorted(grouped.items(), reverse=True))
    
    def group_posts_by_year_and_collection(self, posts: List[Dict]) -> OrderedDict:
        """按年份和合集分组文章，collections和single posts按日期混合排序
        
        Returns:
            OrderedDict: {
                year: {
                    'mixed_items': [  # Mixed list of collections and posts sorted by date
                        {
                            'type': 'collection',
                            'name': str,
                            'posts': [post1, post2, ...],
                            'latest_date': datetime,
                            'count': int
                        },
                        {
                            'type': 'post',
                            'data': post_dict
                        },
                        ...
                    ]
                }
            }
        """
        grouped_by_year = defaultdict(lambda: {'collections': defaultdict(lambda: {'posts': [], 'latest_date': None, 'count': 0}), 'single_posts': []})
        
        for post in posts:
            year = post['year']
            collection = post.get('collection')  # Get collection name from front matter
            
            if collection:
                # Add collection_order for sorting, default to 0 if not specified
                if 'collection_order' not in post:
                    post['collection_order'] = 0
                grouped_by_year[year]['collections'][collection]['posts'].append(post)
                
                # Update latest_date
                current_latest = grouped_by_year[year]['collections'][collection]['latest_date']
                if current_latest is None or post['date'] > current_latest:
                    grouped_by_year[year]['collections'][collection]['latest_date'] = post['date']
                
                # Update count
                grouped_by_year[year]['collections'][collection]['count'] += 1
            else:
                grouped_by_year[year]['single_posts'].append(post)
        
        # Sort posts within each collection by collection_order (ascending), then by date (descending)
        for year_data in grouped_by_year.values():
            for collection_name, collection_data in year_data['collections'].items():
                collection_data['posts'].sort(key=lambda x: (x.get('collection_order', 0), -x['date'].timestamp()))
        
        # Merge collections and single posts, sort by date
        result = OrderedDict()
        for year in sorted(grouped_by_year.keys(), reverse=True):
            year_data = grouped_by_year[year]
            mixed_items = []
            
            # Add collections as items
            for collection_name, collection_data in year_data['collections'].items():
                mixed_items.append({
                    'type': 'collection',
                    'name': collection_name,
                    'posts': collection_data['posts'],
                    'latest_date': collection_data['latest_date'],
                    'count': collection_data['count']
                })
            
            # Add single posts as items
            for post in year_data['single_posts']:
                mixed_items.append({
                    'type': 'post',
                    'data': post
                })
            
            # Sort items by date (collection uses latest_date, post uses date)
            mixed_items.sort(key=lambda x: x['latest_date'] if x['type'] == 'collection' else x['data']['date'], reverse=True)
            
            result[year] = {'mixed_items': mixed_items}
        
        return result
    
    def group_posts_by_tags(self, posts: List[Dict]) -> Dict[str, List[Dict]]:
        """根据指定文章列表获取所有标签及对应的文章"""
        tags = defaultdict(list)
        
        for post in posts:
            for tag in post.get('tags', []):
                tags[tag].append(post)
        
        # 对每个标签下的文章按日期从小到大排序
        for tag in tags:
            tags[tag].sort(key=lambda x: x['date'])
        
        # 按标签名排序
        return dict(sorted(tags.items()))
    
    def get_all_tags(self) -> Dict[str, List[Dict]]:
        """获取所有标签及对应的文章"""
        # 注意：这个方法返回所有文章的标签，不考虑可见性过滤
        # 如果需要根据登录状态过滤标签，应该使用get_tags_by_visibility方法
        posts = self.get_all_posts()
        tags = defaultdict(list)
        
        for post in posts:
            for tag in post.get('tags', []):
                tags[tag].append(post)
        
        # 对每个标签下的文章按日期从小到大排序
        for tag in tags:
            tags[tag].sort(key=lambda x: x['date'])
        
        # 按标签名排序
        return dict(sorted(tags.items()))
    
    def get_tags_by_visibility(self, is_logged_in: bool = False) -> Dict[str, List[Dict]]:
        """根据登录状态获取可见文章的标签"""
        posts = self.get_posts_by_visibility(is_logged_in)
        tags = defaultdict(list)
        
        for post in posts:
            # 确保tags字段存在且不为None
            post_tags = post.get('tags', [])
            if post_tags is None:
                post_tags = []
            for tag in post_tags:
                tags[tag].append(post)
        
        # 对每个标签下的文章按日期从小到大排序
        for tag in tags:
            tags[tag].sort(key=lambda x: x['date'])
        
        # 按标签名排序
        return dict(sorted(tags.items()))
    
    def get_posts_by_tag(self, tag: str) -> List[Dict]:
        """获取指定标签的文章"""
        posts = self.get_all_posts()
        return [post for post in posts if tag in post.get('tags', [])]
    
    def get_posts_by_tag_with_visibility(self, tag: str, is_logged_in: bool = False) -> List[Dict]:
        """根据标签和登录状态获取文章"""
        posts = self.get_posts_by_visibility(is_logged_in)
        return [post for post in posts if tag in post.get('tags', [])]
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """获取最近的文章"""
        posts = self.get_all_posts()
        return posts[:limit]
    
    def get_page_content(self, filename: str) -> Optional[Dict]:
        """获取页面内容（about.md等）"""
        # 检查缓存
        if filename in self._page_cache:
            return self._page_cache[filename]
            
        filepath = os.path.join(self.pages_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                page = frontmatter.load(f)
            
            page_data = {
                'title': page.metadata.get('title', filename.replace('.md', '').title()),
                'content': page.content,
                'layout': page.metadata.get('layout', 'page'),
                'metadata': page.metadata
            }
            
            # 缓存结果
            self._page_cache[filename] = page_data
            return page_data
            
        except Exception as e:
            print(f"Error loading page {filename}: {e}")
            return None
    
    def get_rendered_post_content(self, year: int, month: int, slug: str, markdown_parser) -> Optional[str]:
        """获取渲染后的文章HTML内容（带缓存）"""
        cache_key = f"{year}-{month:02d}-{slug}"
        
        # 检查缓存
        if cache_key in self._rendered_cache:
            return self._rendered_cache[cache_key]
        
        # 获取文章数据
        post = self.get_post_by_slug(year, month, slug)
        if not post:
            return None
        
        # 渲染markdown
        rendered_content = markdown_parser.render(post['content'])
        
        # 缓存结果
        self._rendered_cache[cache_key] = rendered_content
        
        return rendered_content
    
    def get_rendered_page_content(self, filename: str, markdown_parser) -> Optional[str]:
        """获取渲染后的页面HTML内容（带缓存）"""
        cache_key = f"page_{filename}"
        
        # 检查缓存
        if cache_key in self._rendered_cache:
            return self._rendered_cache[cache_key]
        
        # 获取页面数据
        page = self.get_page_content(filename)
        if not page:
            return None
        
        # 渲染markdown
        rendered_content = markdown_parser.render(page['content'])
        
        # 缓存结果
        self._rendered_cache[cache_key] = rendered_content
        
        return rendered_content
    
    def save_post_content(self, filepath: str, content: str) -> bool:
        """保存文章内容到文件"""
        try:
            # 创建备份文件
            backup_path = filepath + '.backup'
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
            
            # 保存新内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 清除相关缓存
            self._posts_cache = None
            self._rendered_cache.clear()
            self._page_cache.clear()
            
            # 删除备份文件（保存成功后）
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            logger.info(f"Successfully saved post content to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving post content to {filepath}: {e}")
            
            # 如果保存失败，尝试恢复备份
            backup_path = filepath + '.backup'
            if os.path.exists(backup_path):
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_content = f.read()
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(backup_content)
                    os.remove(backup_path)
                    logger.info(f"Restored backup for {filepath}")
                except Exception as restore_error:
                    logger.error(f"Failed to restore backup for {filepath}: {restore_error}")
            
            return False

    def sync_blog(self) -> bool:
        """执行博客同步脚本"""
        try:
            blog_root = os.path.dirname(os.path.dirname(__file__))
            update_script = os.path.join(blog_root, 'update.sh')
            
            if not os.path.exists(update_script):
                logger.error(f"Update script not found: {update_script}")
                return False
            
            # 切换到博客根目录并执行update.sh
            result = subprocess.run(
                ['bash', update_script], 
                cwd=blog_root,
                capture_output=True, 
                text=True, 
                timeout=30  # 减少超时时间以避免卡住
            )
            
            if result.returncode == 0:
                logger.info("Blog sync completed successfully")
                logger.info(f"Output: {result.stdout.strip()}")
                return True
            else:
                error_msg = result.stderr.strip()
                logger.error(f"Blog sync failed: {error_msg}")
                # Check if it's an SSH connection error
                if "kex_exchange_identification" in error_msg or "Connection reset by peer" in error_msg:
                    logger.error("SSH connection issue detected. This may be due to network problems or SSH key configuration issues.")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Blog sync timeout")
            return False
        except Exception as e:
            logger.error(f"Error during blog sync: {e}")
            return False
