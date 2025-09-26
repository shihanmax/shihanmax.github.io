#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录解析器
基于Markdown原文解析生成目录结构，支持层级显示
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TOCItem:
    """目录项"""
    level: int
    title: str
    anchor: str
    children: Optional[List['TOCItem']] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class TOCParser:
    """目录解析器"""
    
    def __init__(self):
        # 标题正则表达式，匹配 # 开头的标题
        # 修复：确保正则表达式正确处理包含代码块的Markdown
        self.heading_pattern = re.compile(
            r'^(#{1,6})\s+(.+)$', re.MULTILINE
        )
        
    def parse_markdown_toc(self, markdown_content: str) -> List[TOCItem]:
        """
        从Markdown内容解析目录
        
        Args:
            markdown_content: Markdown原文内容
            
        Returns:
            目录项列表
        """
        if not markdown_content:
            return []
        
        # 查找所有标题
        headings = self.heading_pattern.findall(markdown_content)
        
        if not headings:
            return []
        
        # 转换为TOCItem对象
        toc_items = []
        for i, (hashes, title) in enumerate(headings):
            level = len(hashes)
            # 修复：清理标题文本，去除可能的代码块标记
            clean_title = self._clean_title(title)
            anchor = self._generate_anchor(clean_title, i)
            
            toc_item = TOCItem(
                level=level,
                title=clean_title.strip(),
                anchor=anchor
            )
            toc_items.append(toc_item)
        
        # 构建层级结构
        return self._build_hierarchy(toc_items)
    
    def _clean_title(self, title: str) -> str:
        """
        清理标题文本，去除多余的格式标记
        
        Args:
            title: 原始标题文本
            
        Returns:
            清理后的标题文本
        """
        # 去除行尾的多余空格
        title = title.strip()
        
        # 去除可能的代码标记（如伪代码中的标记）
        # 移除行内代码标记
        title = re.sub(r'`([^`]+)`', r'\1', title)
        
        return title
    
    def _generate_anchor(self, title: str, index: int) -> str:
        """
        生成锚点ID
        
        Args:
            title: 标题文本
            index: 标题索引
            
        Returns:
            锚点ID
        """
        # 清理标题，生成URL友好的锚点
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        anchor = anchor.strip('-')
        
        # 如果锚点为空或重复，使用索引
        if not anchor:
            anchor = f"heading-{index}"
        
        return anchor
    
    def _build_hierarchy(self, flat_items: List[TOCItem]) -> List[TOCItem]:
        """
        将扁平的目录项构建为层级结构
        
        Args:
            flat_items: 扁平的目录项列表
            
        Returns:
            层级结构的目录项列表
        """
        if not flat_items:
            return []
        
        # 使用栈来构建层级结构
        stack = []
        result = []
        
        for item in flat_items:
            # 弹出层级大于等于当前项的所有项
            while stack and stack[-1].level >= item.level:
                stack.pop()
            
            if stack:
                # 当前项是栈顶项的子项
                stack[-1].children.append(item)
            else:
                # 当前项是顶级项
                result.append(item)
            
            # 将当前项压入栈
            stack.append(item)
        
        return result
    
    def generate_toc_html(self, toc_items: List[TOCItem], 
                          collapsed: bool = False) -> str:
        """
        生成目录HTML
        
        Args:
            toc_items: 目录项列表
            collapsed: 是否默认折叠
            
        Returns:
            HTML字符串
        """
        if not toc_items:
            return ""
        
        collapsed_class = " collapsed" if collapsed else ""
        html = f'<ul class="toc-list{collapsed_class}">'
        html += self._render_toc_items(toc_items)
        html += '</ul>'
        
        return html
    
    def _render_toc_items(self, items: List[TOCItem]) -> str:
        """渲染目录项"""
        html = ""
        
        for item in items:
            html += f'<li class="level-{item.level}">'
            html += (f'<a href="#{item.anchor}" '
                     f'data-target="{item.anchor}" class="toc-link">')
            html += f'{item.title}</a>'
            
            if item.children:
                html += '<ul class="toc-sublist">'
                html += self._render_toc_items(item.children)
                html += '</ul>'
            
            html += '</li>'
        
        return html
    
    def generate_toc_json(self, toc_items: List[TOCItem]) -> List[Dict]:
        """
        生成目录JSON数据
        
        Args:
            toc_items: 目录项列表
            
        Returns:
            JSON格式的目录数据
        """
        def item_to_dict(item: TOCItem) -> Dict:
            children_data = []
            if item.children:
                children_data = [
                    item_to_dict(child) for child in item.children
                ]
            
            return {
                'level': item.level,
                'title': item.title,
                'anchor': item.anchor,
                'children': children_data
            }
        
        return [item_to_dict(item) for item in toc_items]
    
    def get_toc_summary(self, toc_items: List[TOCItem]) -> Dict:
        """
        获取目录摘要信息
        
        Args:
            toc_items: 目录项列表
            
        Returns:
            目录摘要信息
        """
        def count_items(items: List[TOCItem]) -> Tuple[int, int]:
            total = len(items)
            max_level = max((item.level for item in items), default=0)
            
            for item in items:
                if item.children:
                    child_total, child_max_level = count_items(item.children)
                    total += child_total
                    max_level = max(max_level, child_max_level)
            
            return total, max_level
        
        total_items, max_level = count_items(toc_items)
        
        return {
            'total_items': total_items,
            'max_level': max_level,
            'has_content': total_items > 0
        }