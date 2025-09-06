/**
 * Markdown编辑器 - 实时预览和保存功能
 */

class MarkdownEditor {
    constructor() {
        this.editor = document.getElementById('markdown-editor');
        this.preview = document.getElementById('preview-content');
        this.saveBtn = document.getElementById('save-btn');
        this.saveStatus = document.getElementById('save-status');
        this.charCount = document.getElementById('char-count');
        this.wordCount = document.getElementById('word-count');
        
        this.isDirty = false;
        this.isPreviewLoading = false;
        this.lastContent = this.editor.value;
        this.previewTimeout = null;
        this.scrollSyncEnabled = true;
        this.cursorSyncEnabled = true;
        this.highlightTimeout = null;
        
        // 删除未使用的滚动同步相关属性
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateCounters();
        this.loadInitialPreview();
        this.setupAutoSave();
        this.setupScrollSync();
        this.setupCursorSync();
        this.preventPreviewInteraction();
    }
    
    // 防止预览区域的交互引起跳转
    preventPreviewInteraction() {
        // 移除预览区域中所有链接的点击事件
        this.preview.addEventListener('click', (e) => {
            // 防止所有链接点击
            if (e.target.tagName === 'A') {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
            
            // 防止标题点击导致的跳转
            const heading = e.target.closest('h1, h2, h3, h4, h5, h6');
            if (heading) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
        
        // 防止鼠标右键菜单引起的意外交互
        this.preview.addEventListener('contextmenu', (e) => {
            // 允许右键菜单，但不允许其他交互
        });
    }

    bindEvents() {
        // 编辑器内容变化事件
        this.editor.addEventListener('input', () => {
            this.onContentChange();
        });

        // 保存按钮点击事件
        this.saveBtn.addEventListener('click', () => {
            this.saveContent();
        });

        // 刷新预览按钮
        document.getElementById('refresh-preview').addEventListener('click', () => {
            this.updatePreview(true);
        });

        // 格式化工具栏按钮
        this.bindFormatButtons();

        // 键盘快捷键
        this.bindKeyboardShortcuts();

        // 防止意外离开页面
        window.addEventListener('beforeunload', (e) => {
            if (this.isDirty) {
                e.preventDefault();
                e.returnValue = '您有未保存的更改，确定要离开吗？';
                return e.returnValue;
            }
        });
    }

    bindFormatButtons() {
        // 粗体
        document.getElementById('format-bold').addEventListener('click', () => {
            this.wrapSelection('**', '**');
        });

        // 斜体
        document.getElementById('format-italic').addEventListener('click', () => {
            this.wrapSelection('*', '*');
        });

        // 链接
        document.getElementById('format-link').addEventListener('click', () => {
            const url = prompt('请输入链接地址:');
            if (url) {
                const text = this.getSelectedText() || '链接文本';
                this.replaceSelection(`[${text}](${url})`);
            }
        });

        // 代码
        document.getElementById('format-code').addEventListener('click', () => {
            const selection = this.getSelectedText();
            if (selection.includes('\n')) {
                // 多行代码块
                this.wrapSelection('```\n', '\n```');
            } else {
                // 行内代码
                this.wrapSelection('`', '`');
            }
        });

        // 数学公式
        document.getElementById('format-math').addEventListener('click', () => {
            const selection = this.getSelectedText();
            if (selection.includes('\n')) {
                // 块级公式
                this.wrapSelection('$$\n', '\n$$');
            } else {
                // 行内公式
                this.wrapSelection('$', '$');
            }
        });
        
        // 删除滚动同步和光标同步按钮相关的事件监听器
    }

    bindKeyboardShortcuts() {
        this.editor.addEventListener('keydown', (e) => {
            // Ctrl+S 保存
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveContent();
            }
            
            // Ctrl+B 粗体
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                this.wrapSelection('**', '**');
            }
            
            // Ctrl+I 斜体
            if (e.ctrlKey && e.key === 'i') {
                e.preventDefault();
                this.wrapSelection('*', '*');
            }
            
            // Tab 键处理
            if (e.key === 'Tab') {
                e.preventDefault();
                this.insertAtCursor('    '); // 4个空格
            }
        });
    }

    onContentChange() {
        const currentContent = this.editor.value;
        
        // 更新计数器
        this.updateCounters();
        
        // 标记为已修改
        if (currentContent !== this.lastContent) {
            this.markAsDirty();
        }
        
        // 延迟更新预览
        this.schedulePreviewUpdate();
    }

    markAsDirty() {
        this.isDirty = true;
        this.saveBtn.disabled = false;
        this.saveStatus.textContent = '未保存的更改';
        this.saveStatus.className = 'status-dirty';
    }

    markAsClean() {
        this.isDirty = false;
        this.saveBtn.disabled = true;
        this.saveStatus.textContent = '已保存';
        this.saveStatus.className = 'status-clean';
        this.lastContent = this.editor.value;
    }

    updateCounters() {
        const content = this.editor.value;
        const charCount = content.length;
        const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
        
        this.charCount.textContent = `字符数: ${charCount}`;
        this.wordCount.textContent = `单词数: ${wordCount}`;
    }

    schedulePreviewUpdate() {
        // 清除之前的延迟任务
        if (this.previewTimeout) {
            clearTimeout(this.previewTimeout);
        }
        
        // 延迟500ms更新预览
        this.previewTimeout = setTimeout(() => {
            this.updatePreview();
        }, 500);
    }

    async updatePreview(force = false) {
        const content = this.editor.value;
        
        // 如果内容没有变化且不是强制更新，则跳过
        if (!force && content === this.lastPreviewContent) {
            return;
        }
        
        // 如果正在加载预览，跳过
        if (this.isPreviewLoading) {
            return;
        }
        
        this.isPreviewLoading = true;
        this.lastPreviewContent = content;
        
        try {
            // 显示加载状态
            this.preview.innerHTML = '<div class=\"preview-loading\">正在渲染预览...</div>';
            
            const response = await fetch(window.postData.previewUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 保存当前预览的滚动位置
                const currentPreviewScrollTop = this.preview.scrollTop;
                
                this.preview.innerHTML = result.html;
                
                // 重新初始化MathJax（如果有数学公式）
                if (window.MathJax && window.MathJax.typesetPromise) {
                    await window.MathJax.typesetPromise([this.preview]);
                }
                
                // 重新高亮代码块
                if (window.hljs) {
                    this.preview.querySelectorAll('pre code').forEach((block) => {
                        window.hljs.highlightBlock(block);
                    });
                }
                
                // 恢复预览的滚动位置（防止跳到顶部）
                if (!force) {
                    // 等待DOM更新完成后恢复位置
                    requestAnimationFrame(() => {
                        this.preview.scrollTop = currentPreviewScrollTop;
                        // 然后处理同步操作
                        this.handlePostUpdateSync();
                    });
                } else {
                    // 强制更新时不进行同步操作
                }
            } else {
                this.preview.innerHTML = `<div class=\"preview-error\">预览失败: ${result.error}</div>`;
            }
        } catch (error) {
            console.error('Preview update failed:', error);
            this.preview.innerHTML = `<div class=\"preview-error\">预览失败: ${error.message}</div>`;
        } finally {
            this.isPreviewLoading = false;
        }
    }

    async loadInitialPreview() {
        await this.updatePreview(true);
    }

    async saveContent() {
        if (!this.isDirty) {
            return;
        }
        
        const content = this.editor.value;
        
        try {
            // 更新保存状态
            this.saveStatus.textContent = '正在保存...';
            this.saveStatus.className = 'status-saving';
            this.saveBtn.disabled = true;
            
            const response = await fetch(window.postData.saveUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.markAsClean();
                this.showNotification('保存成功！', 'success');
            } else {
                throw new Error(result.error || '保存失败');
            }
        } catch (error) {
            console.error('Save failed:', error);
            this.saveStatus.textContent = '保存失败';
            this.saveStatus.className = 'status-error';
            this.saveBtn.disabled = false;
            this.showNotification(`保存失败: ${error.message}`, 'error');
        }
    }

    setupScrollSync() {
        // 禁用滚动同步功能
        // 不再监听编辑器滚动事件
        // 不再监听预览区滚动事件
        
        // 只保留点击事件监听，用于居中滚动
        this.editor.addEventListener('click', () => {
            if (this.cursorSyncEnabled) {
                // 延迟一点执行，确保光标位置已更新
                setTimeout(() => {
                    this.scrollPreviewToCenter();
                }, 50);
            }
        });
        
        // 监听键盘导航事件
        this.editor.addEventListener('keyup', (e) => {
            if (this.cursorSyncEnabled && ['ArrowUp', 'ArrowDown', 'Home', 'End', 'PageUp', 'PageDown'].includes(e.key)) {
                setTimeout(() => {
                    this.scrollPreviewToCenter();
                }, 50);
            }
        });
    }
    
    // 简化的居中滚动功能
    scrollPreviewToCenter() {
        if (!this.cursorSyncEnabled) return;
        
        const cursorPosition = this.editor.selectionStart;
        const content = this.editor.value;
        
        // 计算当前光标行号
        const currentLine = (content.substring(0, cursorPosition).match(/\n/g) || []).length;
        const lines = content.split('\n');
        const currentLineText = lines[currentLine] || '';
        
        // 查找对应的预览元素
        const targetElement = this.findPreviewElementForLine(currentLine);
        
        if (targetElement) {
            // 高亮目标元素
            this.clearPreviousHighlight();
            targetElement.classList.add('cursor-highlight');
            
            // 滚动到居中位置
            this.scrollElementToCenter(targetElement);
            
            // 1秒后移除高亮
            if (this.highlightTimeout) {
                clearTimeout(this.highlightTimeout);
            }
            
            this.highlightTimeout = setTimeout(() => {
                if (targetElement.classList.contains('cursor-highlight')) {
                    targetElement.classList.remove('cursor-highlight');
                }
            }, 1000);
        }
    }

    // 将元素滚动到预览区域的居中位置
    scrollElementToCenter(element) {
        if (!element) return;
        
        const previewContainer = this.preview;
        const elementTop = element.offsetTop;
        const containerHeight = previewContainer.clientHeight;
        const elementHeight = element.offsetHeight;
        
        // 计算居中位置
        const centerPosition = elementTop - (containerHeight / 2) + (elementHeight / 2);
        
        // 确保不会滚动到负值或超出范围
        const maxScroll = previewContainer.scrollHeight - containerHeight;
        const targetScrollTop = Math.max(0, Math.min(centerPosition, maxScroll));
        
        // 平滑滚动到目标位置
        this.smoothScrollTo(targetScrollTop);
    }
    
    setupCursorSync() {
        // 简化光标同步：只在点击和键盘导航时触发
        
        // 点击事件已在 setupScrollSync 中处理
        
        // 键盘事件已在 setupScrollSync 中处理
        
        // 不再监听 selectionchange 事件，避免输入时的频繁触发
    }

    
    clearPreviousHighlight() {
        const highlightedElements = this.preview.querySelectorAll('.cursor-highlight');
        highlightedElements.forEach(element => {
            element.classList.remove('cursor-highlight');
        });
        
        if (this.highlightTimeout) {
            clearTimeout(this.highlightTimeout);
            this.highlightTimeout = null;
        }
    }
    
    // 查找预览中对应的元素
    findPreviewElementForLine(currentLineNumber) {
        const lines = this.editor.value.split('\n');
        const currentLine = lines[currentLineNumber] || '';
        
        // 获取光标位置
        const cursorPosition = this.editor.selectionStart;
        const textBeforeCursor = this.editor.value.substring(0, cursorPosition);
        
        // 计算光标在当前行的位置
        const lineStart = textBeforeCursor.lastIndexOf('\n') + 1;
        const columnPosition = cursorPosition - lineStart;
        
        // 提取光标前后的子串
        const substring = this.extractSubstring(currentLine, columnPosition, 12);
        
        console.log(`当前行: ${currentLineNumber}, 子串: "${substring}"`);
        
        if (!substring.trim()) {
            console.log('子串为空，返回null');
            return null;
        }
        
        // 在预览中搜索匹配的元素
        const result = this.findMatchingElement(substring);
        console.log('匹配结果:', result);
        return result;
    }
    
    // 提取光标位置周围的子串
    extractSubstring(line, cursorPosition, initialLength) {
        const start = Math.max(0, cursorPosition - Math.floor(initialLength / 2));
        const end = Math.min(line.length, cursorPosition + Math.floor(initialLength / 2));
        return line.substring(start, end);
    }
    
    // 在预览中查找匹配的元素
    findMatchingElement(initialSubstring) {
        let substring = initialSubstring;
        let substringLength = 12;
        const maxAttempts = 5;
        
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            const matches = this.searchInPreview(substring);
            console.log(`第${attempt + 1}次尝试, 子串: "${substring}", 匹配数: ${matches.length}`);
            
            if (matches.length === 1) {
                console.log('找到唯一匹配，返回结果');
                return matches[0];
            } else if (matches.length === 0) {
                // 没有匹配，尝试减少子串长度
                if (substring.length > 3) {
                    substring = substring.substring(1, substring.length - 1);
                    continue;
                } else {
                    console.log('没有找到匹配，返回null');
                    return null;
                }
            } else if (matches.length > 1 && attempt < maxAttempts - 1) {
                // 多个匹配，增加子串长度
                substringLength += 5;
                const cursorPosition = Math.floor(substring.length / 2);
                const lineContent = this.getCurrentLineContent();
                if (lineContent) {
                    substring = this.extractSubstring(lineContent, cursorPosition, substringLength);
                }
            } else {
                // 最后一次尝试或无法扩展，返回第一个匹配
                console.log('返回第一个匹配结果');
                return matches[0];
            }
        }
        
        console.log('超过最大尝试次数，返回null');
        return null;
    }
    



    setupAutoSave() {
        // 每30秒自动保存一次（如果有更改）
        setInterval(() => {
            if (this.isDirty) {
                this.saveContent();
            }
        }, 30000);
    }
    
    // 简化的更新后处理（只做必要的清理）
    handlePostUpdateSync() {
        // 清除之前的延迟任务
        if (this.updateSyncTimeout) {
            clearTimeout(this.updateSyncTimeout);
        }
        
        // 简化处理，不进行自动同步
        this.isSyncingAfterUpdate = true;
        
        this.updateSyncTimeout = setTimeout(() => {
            // 只重新设置光标同步，不进行自动滚动
            if (this.cursorSyncEnabled) {
                this.clearPreviousHighlight();
                // 不自动触发光标同步，等待用户下次移动光标
            }
            
            // 结束更新后同步标记
            this.isSyncingAfterUpdate = false;
        }, 100);
    }
    
    // 在预览中搜索子串
    searchInPreview(substring) {
        const matches = [];
        const cleanSubstring = substring.trim();
        
        if (!cleanSubstring) {
            return matches;
        }
        
        // 遍历预览中的所有文本节点
        const walker = document.createTreeWalker(
            this.preview,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            const text = node.textContent;
            if (text.includes(cleanSubstring)) {
                // 找到包含子串的文本节点，获取其最近的有意义元素
                let element = node.parentElement;
                
                // 向上查找到合适的容器元素
                while (element && element !== this.preview) {
                    if (this.isValidTargetElement(element)) {
                        if (!matches.includes(element)) {
                            matches.push(element);
                        }
                        break;
                    }
                    element = element.parentElement;
                }
            }
        }
        
        return matches;
    }
    
    // 判断是否是有效的目标元素
    isValidTargetElement(element) {
        const tagName = element.tagName.toLowerCase();
        
        // 排除不适合的元素
        if (['script', 'style', 'meta', 'link'].includes(tagName)) {
            return false;
        }
        
        // 优先选择语义化元素
        if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'blockquote', 'pre', 'code'].includes(tagName)) {
            return true;
        }
        
        // 其他块级元素也可以接受
        const style = window.getComputedStyle(element);
        return style.display === 'block' || style.display === 'list-item';
    }
    
    // 获取当前行内容
    getCurrentLineContent() {
        const cursorPosition = this.editor.selectionStart;
        const textBeforeCursor = this.editor.value.substring(0, cursorPosition);
        const lineStart = textBeforeCursor.lastIndexOf('\n') + 1;
        const lineEnd = this.editor.value.indexOf('\n', cursorPosition);
        const actualLineEnd = lineEnd === -1 ? this.editor.value.length : lineEnd;
        
        return this.editor.value.substring(lineStart, actualLineEnd);
    }

    // 新增：平滑滚动到指定位置
    smoothScrollTo(targetScrollTop) {
        const currentScrollTop = this.preview.scrollTop;
        const distance = targetScrollTop - currentScrollTop;
        
        // 如果距离太小，直接设置
        if (Math.abs(distance) < 10) {
            this.preview.scrollTop = targetScrollTop;
            return;
        }
        
        // 渐进式滚动
        const duration = Math.min(300, Math.abs(distance) * 2); // 动态调整持续时间
        const startTime = performance.now();
        
        const scroll = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 使用easeOutCubic缓动函数
            const eased = 1 - Math.pow(1 - progress, 3);
            
            this.preview.scrollTop = currentScrollTop + distance * eased;
            
            if (progress < 1) {
                requestAnimationFrame(scroll);
            }
        };
        
        requestAnimationFrame(scroll);
    }

    // 文本操作辅助方法
    getSelectedText() {
        const start = this.editor.selectionStart;
        const end = this.editor.selectionEnd;
        return this.editor.value.substring(start, end);
    }

    replaceSelection(replacement) {
        const start = this.editor.selectionStart;
        const end = this.editor.selectionEnd;
        const value = this.editor.value;
        
        this.editor.value = value.substring(0, start) + replacement + value.substring(end);
        
        // 设置光标位置
        const newPos = start + replacement.length;
        this.editor.setSelectionRange(newPos, newPos);
        this.editor.focus();
        
        this.onContentChange();
    }

    wrapSelection(before, after) {
        const selection = this.getSelectedText();
        const replacement = before + selection + after;
        this.replaceSelection(replacement);
        
        // 如果没有选中文本，将光标放在包装符之间
        if (!selection) {
            const start = this.editor.selectionStart;
            const newPos = start - after.length;
            this.editor.setSelectionRange(newPos, newPos);
        }
    }

    insertAtCursor(text) {
        const start = this.editor.selectionStart;
        const value = this.editor.value;
        
        this.editor.value = value.substring(0, start) + text + value.substring(start);
        
        const newPos = start + text.length;
        this.editor.setSelectionRange(newPos, newPos);
        this.editor.focus();
        
        this.onContentChange();
    }

    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // 3秒后移除
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// 页面加载完成后初始化编辑器
document.addEventListener('DOMContentLoaded', function() {
    // 检查管理员状态并显示编辑功能
    checkAdminStatus();
    
    // 初始化编辑器
    window.markdownEditor = new MarkdownEditor();
});

// 检查管理员状态的函数（复用之前的逻辑）
async function checkAdminStatus() {
    try {
        const response = await fetch('/admin/status');
        const result = await response.json();
        
        const adminOnlyElements = document.querySelectorAll('.admin-only');
        adminOnlyElements.forEach(el => {
            el.style.display = result.logged_in ? 'flex' : 'none';
        });
    } catch (error) {
        console.error('Error checking admin status:', error);
    }
}