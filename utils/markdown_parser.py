#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown解析器 - 兼容Jekyll的markdown渲染
支持语法高亮、数学公式、表格等功能
"""

import markdown
from pygments.formatters import HtmlFormatter
import re

class MarkdownParser:
    """Markdown解析器"""
    
    def __init__(self):
        # 配置Markdown扩展
        self.extensions = [
            'markdown.extensions.extra',  # 包含tables, fenced_code等
            'markdown.extensions.codehilite',  # 语法高亮
            'markdown.extensions.toc',  # 目录生成
            'markdown.extensions.nl2br',  # 换行转<br>
            'markdown.extensions.sane_lists',  # 更好的列表支持
        ]
        
        # 配置扩展参数
        self.extension_configs = {
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
                'linenums': True,  # 启用行号
            },
            'markdown.extensions.toc': {
                'permalink': True,
                'permalink_class': 'headerlink',
                'permalink_title': 'Permanent link'
            }
        }
        
        # 初始化Markdown实例
        self.md = markdown.Markdown(
            extensions=self.extensions,
            extension_configs=self.extension_configs
        )
        
        # Pygments HTML formatter - 优化性能配置
        self.formatter = HtmlFormatter(
            style='github-dark',  # 使用预定义的主题
            cssclass='highlight',
            linenos=False,  # 禁用内置行号，通过CSS实现
            noclasses=False,  # 使用CSS类而不是内联样式
        )
    
    def render(self, content: str) -> str:
        """渲染Markdown内容为HTML"""
        if not content:
            return ""
        
        # 预处理：处理一些Jekyll特有的语法
        content = self._preprocess_content(content)
        
        # 使用markdown渲染
        html = self.md.convert(content)
        
        # 后处理：添加一些自定义功能
        html = self._postprocess_html(html)
        
        # 重置markdown实例状态
        self.md.reset()
        
        return html
    
    def _preprocess_content(self, content: str) -> str:
        """预处理markdown内容"""
        
        # 初始化公式存储
        self._math_blocks = []
        self._inline_math_blocks = []
        
        # 优化的数学公式处理 - 使用更简单的正则
        # 先处理行间公式（$$...$$ ）
        def preserve_display_math(match):
            formula = match.group(0)
            self._math_blocks.append(formula)
            return f'MATHBLOCK{len(self._math_blocks)-1}ENDMATH'
        
        # 再处理行内公式（$...$）
        def preserve_inline_math(match):
            formula = match.group(0)
            self._inline_math_blocks.append(formula)
            return f'INLINEMATH{len(self._inline_math_blocks)-1}ENDINLINE'
        
        # 用更高效的正则处理数学公式
        content = re.sub(r'\$\$[^$]*?\$\$', preserve_display_math, content, flags=re.DOTALL)
        content = re.sub(r'(?<!\\)\$([^$\n]+?)\$', preserve_inline_math, content)
        
        # 简化Jekyll标签处理
        content = re.sub(r'{%\s*highlight\s+(\w+)\s*%}([\s\S]*?){%\s*endhighlight\s*%}', r'```\1\2```', content)
        content = re.sub(r'{[%{].*?[%}]}', '', content)  # 移除其他Jekyll标签
        
        return content
    
    def _restore_math_formulas(self, html: str) -> str:
        """恢复数学公式"""
        
        # 恢复行间公式
        if hasattr(self, '_math_blocks') and self._math_blocks:
            for i, math_block in enumerate(self._math_blocks):
                placeholder = f'MATHBLOCK{i}ENDMATH'
                if placeholder in html:
                    html = html.replace(placeholder, math_block)
        
        # 恢复行内公式
        if hasattr(self, '_inline_math_blocks') and self._inline_math_blocks:
            for i, math_block in enumerate(self._inline_math_blocks):
                placeholder = f'INLINEMATH{i}ENDINLINE'
                if placeholder in html:
                    html = html.replace(placeholder, math_block)
        
        return html
    
    def _postprocess_html(self, html: str) -> str:
        """后处理HTML内容"""
        
        # 恢复数学公式
        html = self._restore_math_formulas(html)
        
        # 为表格添加responsive wrapper
        html = re.sub(
            r'<table>',
            '<div class="table-responsive"><table class="table">',
            html
        )
        html = re.sub(
            r'</table>',
            '</table></div>',
            html
        )
        
        # 为图片添加responsive class
        html = re.sub(
            r'<img([^>]*?)>',
            r'<img class="img-responsive"\1>',
            html
        )
        
        return html
    
    def _add_line_numbers_to_code_blocks(self, html: str) -> str:
        """为代码块添加行号"""
        def add_line_numbers(match):
            code_block = match.group(0)
            if 'class="highlight"' in code_block:
                # 提取代码内容
                code_content = re.search(r'<code[^>]*>(.*?)</code>', code_block, re.DOTALL)
                if code_content:
                    lines = code_content.group(1).split('\n')
                    numbered_lines = []
                    for i, line in enumerate(lines, 1):
                        if line.strip():  # 只为非空行添加行号
                            numbered_lines.append(f'<span class="line-number">{i:2d}</span>{line}')
                        else:
                            numbered_lines.append(line)
                    
                    numbered_code = '\n'.join(numbered_lines)
                    code_block = re.sub(
                        r'<code[^>]*>.*?</code>',
                        f'<code>{numbered_code}</code>',
                        code_block,
                        flags=re.DOTALL
                    )
            return code_block
        
        return re.sub(r'<div class="highlight">.*?</div>', add_line_numbers, html, flags=re.DOTALL)
    
    def get_toc(self, content: str) -> str:
        """获取目录"""
        # 渲染内容以生成目录
        self.render(content)
        toc = self.md.toc
        self.md.reset()
        return toc
    
    def extract_summary(self, content: str, length: int = 200) -> str:
        """提取文章摘要"""
        # 先渲染为HTML
        html = self.render(content)
        
        # 移除HTML标签
        import re
        text = re.sub(r'<[^>]+>', '', html)
        
        # 截取指定长度
        if len(text) <= length:
            return text
        
        # 在单词边界截断
        truncated = text[:length]
        last_space = truncated.rfind(' ')
        if last_space > length * 0.8:  # 如果最后一个空格不太远
            truncated = truncated[:last_space]
        
        return truncated + '...'