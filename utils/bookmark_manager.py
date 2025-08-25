#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签管理器
处理书签数据的增删改查功能
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class BookmarkManager:
    """书签管理器类"""
    
    def __init__(self, data_file: str = None):
        """
        初始化书签管理器
        
        Args:
            data_file: 书签数据文件路径，默认为data/bookmarks.json
        """
        if data_file is None:
            # 默认数据文件路径
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            self.data_file = os.path.join(self.data_dir, 'bookmarks.json')
        else:
            self.data_file = data_file
            self.data_dir = os.path.dirname(self.data_file)
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化数据文件
        self._init_data_file()
    
    def _init_data_file(self):
        """初始化数据文件，如果不存在则创建"""
        if not os.path.exists(self.data_file):
            initial_data = {
                "bookmarks": [
                    {
                        "id": 1,
                        "title": "GitHub",
                        "url": "https://github.com",
                        "description": "代码托管平台",
                        "tags": ["代码", "开源", "版本控制"],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "title": "Stack Overflow",
                        "url": "https://stackoverflow.com",
                        "description": "程序员问答社区",
                        "tags": ["问答", "编程", "技术"],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                ],
                "next_id": 3
            }
            self._save_data(initial_data)
    
    def _load_data(self) -> Dict:
        """加载书签数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或损坏，重新初始化
            self._init_data_file()
            return self._load_data()
    
    def _save_data(self, data: Dict):
        """保存书签数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_all_bookmarks(self) -> List[Dict]:
        """获取所有书签"""
        data = self._load_data()
        return data.get('bookmarks', [])
    
    def get_bookmark_by_id(self, bookmark_id: int) -> Optional[Dict]:
        """根据ID获取书签"""
        bookmarks = self.get_all_bookmarks()
        for bookmark in bookmarks:
            if bookmark.get('id') == bookmark_id:
                return bookmark
        return None
    
    def get_bookmarks_by_tag(self, tag: str) -> List[Dict]:
        """根据标签获取书签"""
        bookmarks = self.get_all_bookmarks()
        return [b for b in bookmarks if tag in b.get('tags', [])]
    
    def search_bookmarks(self, query: str) -> List[Dict]:
        """搜索书签（标题、描述、标签）"""
        bookmarks = self.get_all_bookmarks()
        query = query.lower()
        results = []
        
        for bookmark in bookmarks:
            # 在标题、描述、标签中搜索
            if (query in bookmark.get('title', '').lower() or
                query in bookmark.get('description', '').lower() or
                any(query in tag.lower() for tag in bookmark.get('tags', []))):
                results.append(bookmark)
        
        return results
    
    def add_bookmark(self, title: str, url: str, description: str = '',
                    tags: List[str] = None) -> Dict:
        """添加新书签"""
        data = self._load_data()
        
        # 生成新ID
        new_id = data.get('next_id', 1)
        data['next_id'] = new_id + 1
        
        # 创建新书签
        new_bookmark = {
            'id': new_id,
            'title': title,
            'url': url,
            'description': description,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 添加到列表
        data['bookmarks'].append(new_bookmark)
        
        # 保存数据
        self._save_data(data)
        
        return new_bookmark
    
    def update_bookmark(self, bookmark_id: int, **kwargs) -> Optional[Dict]:
        """更新书签"""
        data = self._load_data()
        bookmarks = data.get('bookmarks', [])
        
        for i, bookmark in enumerate(bookmarks):
            if bookmark.get('id') == bookmark_id:
                # 更新字段
                for key, value in kwargs.items():
                    if key in ['title', 'url', 'description', 'tags']:
                        bookmark[key] = value
                
                # 更新时间戳
                bookmark['updated_at'] = datetime.now().isoformat()
                
                # 保存数据
                self._save_data(data)
                
                return bookmark
        
        return None
    
    def delete_bookmark(self, bookmark_id: int) -> bool:
        """删除书签"""
        data = self._load_data()
        bookmarks = data.get('bookmarks', [])
        
        for i, bookmark in enumerate(bookmarks):
            if bookmark.get('id') == bookmark_id:
                bookmarks.pop(i)
                self._save_data(data)
                return True
        
        return False
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        bookmarks = self.get_all_bookmarks()
        tags = set()
        for bookmark in bookmarks:
            tags.update(bookmark.get('tags', []))
        return sorted(list(tags))