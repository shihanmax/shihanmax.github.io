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
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateCounters();
        this.loadInitialPreview();
        this.setupAutoSave();
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

    setupAutoSave() {
        // 每30秒自动保存一次（如果有更改）
        setInterval(() => {
            if (this.isDirty) {
                this.saveContent();
            }
        }, 30000);
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