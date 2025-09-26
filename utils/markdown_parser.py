#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown解析器 - 兼容Jekyll的markdown渲染
支持语法高亮、数学公式、表格等功能
"""

import markdown
from pygments.formatters import HtmlFormatter
import re
from .toc_parser import TOCParser


class MarkdownParser:
    """Markdown解析器"""
    
    def __init__(self):
        # 初始化目录解析器
        self.toc_parser = TOCParser()
        
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
        content = re.sub(
            r'\$\$[^$]*?\$\$', 
            preserve_display_math, 
            content, 
            flags=re.DOTALL
        )
        content = re.sub(
            r'(?<!\\)\$([^$\n]+?)\$', 
            preserve_inline_math, 
            content
        )
        
        # 简化Jekyll标签处理
        content = re.sub(
            r'{%\s*highlight\s+(\w+)\s*%}([\s\S]*?){%\s*endhighlight\s*%}', 
            r'```\1\2```', content
        )
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
    
    def _ensure_content_wrapped(self, html: str) -> str:
        """确保HTML内容被正确包装"""
        # 移除可能的首尾空白
        html = html.strip()
        
        # 检查是否已经包装在适当的标签中
        starts_with_valid_tag = (
            html.startswith('<div') or 
            html.startswith('<p') or 
            html.startswith('<h')
        )
        
        if not starts_with_valid_tag:
            # 如果内容没有被适当的标签包装，添加一个包装器
            html = f'<div class="markdown-content">{html}</div>'
        
        return html
    
    def _postprocess_html(self, html: str) -> str:
        """后处理HTML内容"""
        # 添加调试信息
        original_length = len(html)
        
        # 恢复数学公式
        html = self._restore_math_formulas(html)
        
        # 为表格添加responsive wrapper
        # 使用更精确的正则表达式，避免影响代码块中的表格
        html = re.sub(
            r'(<table>)',
            r'<div class="table-responsive"><table class="table">',
            html
        )
        # Only replace </table> that is not followed by </div>
        html = re.sub(
            r'(</table>)(?!</div>)',
            r'</table></div>',
            html
        )
        
        # 为图片添加responsive class
        html = re.sub(
            r'<img([^>]*?)>',
            r'<img class="img-responsive"\1>',
            html
        )
        
        # 修复：确保代码块不会影响后续内容
        # 移除可能存在的多余空白行
        html = re.sub(r'</pre>\s*<pre>', '</pre>\n<pre>', html)
        
        # 确保HTML内容完整，移除首尾空白
        html = html.strip()
        
        # 添加调试信息
        processed_length = len(html)
        if abs(original_length - processed_length) > 1000:
            # 如果长度变化很大，可能是有问题
            msg = ("Warning: HTML length changed significantly "
                   "during postprocessing")
            print(msg)
            print(f"  {original_length} -> {processed_length}")
        
        return html
    
    def _add_line_numbers_to_code_blocks(self, html: str) -> str:
        """为代码块添加行号"""
        def add_line_numbers(match):
            code_block = match.group(0)
            if 'class="highlight"' in code_block:
                # 提取代码内容
                code_content = re.search(
                    r'<code[^>]*>(.*?)</code>', code_block, re.DOTALL
                )
                if code_content:
                    lines = code_content.group(1).split('\n')
                    numbered_lines = []
                    for i, line in enumerate(lines, 1):
                        if line.strip():  # 只为非空行添加行号
                            line_number = (
                                f'<span class="line-number">{i:2d}</span>'
                            )
                            numbered_lines.append(f'{line_number}{line}')
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
        
        return re.sub(
            r'<div class="highlight">.*?</div>', 
            add_line_numbers, html, flags=re.DOTALL
        )
    
    def get_toc(self, content: str) -> str:
        """获取目录"""
        # 直接转换内容以生成目录，不调用render方法避免reset
        self.md.convert(content)
        # 使用hasattr检查toc属性是否存在
        toc = getattr(self.md, 'toc', '') if hasattr(self.md, 'toc') else ''
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
    
    def parse_toc_from_markdown(self, content: str):
        """
        从Markdown内容解析目录
        
        Args:
            content: Markdown原文内容
            
        Returns:
            目录项列表
        """
        return self.toc_parser.parse_markdown_toc(content)
    
    def generate_toc_html(self, content: str, collapsed: bool = False) -> str:
        """
        生成目录HTML
        
        Args:
            content: Markdown原文内容
            collapsed: 是否默认折叠
            
        Returns:
            目录HTML字符串
        """
        toc_items = self.parse_toc_from_markdown(content)
        return self.toc_parser.generate_toc_html(toc_items, collapsed)
    
    def generate_toc_json(self, content: str) -> list:
        """
        生成目录JSON数据
        
        Args:
            content: Markdown原文内容
            
        Returns:
            目录JSON数据
        """
        toc_items = self.parse_toc_from_markdown(content)
        return self.toc_parser.generate_toc_json(toc_items)
    
    def get_toc_summary(self, content: str) -> dict:
        """
        获取目录摘要信息
        
        Args:
            content: Markdown原文内容
            
        Returns:
            目录摘要信息
        """
        toc_items = self.parse_toc_from_markdown(content)
        return self.toc_parser.get_toc_summary(toc_items)