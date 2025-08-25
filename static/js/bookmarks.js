/**
 * 书签页面JavaScript功能
 * 处理书签的增删改查操作
 */

class BookmarkManager {
    constructor() {
        this.currentBookmarkId = null;
        this.isAdmin = false;
        this.init();
    }

    async init() {
        await this.checkAdminStatus();
        this.updateUI();
        this.bindEvents();
        this.setupSearchAndFilter();
    }

    async checkAdminStatus() {
        try {
            const response = await fetch('/admin/status');
            const result = await response.json();
            this.isAdmin = result.logged_in;
        } catch (error) {
            console.error('Error checking admin status:', error);
            this.isAdmin = false;
        }
    }

    updateUI() {
        // 显示/隐藏管理员功能
        const addBtn = document.getElementById('add-bookmark-btn');
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const adminOnlyElements = document.querySelectorAll('.admin-only');

        if (this.isAdmin) {
            if (addBtn) addBtn.style.display = 'block';
            if (loginBtn) loginBtn.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'block';
            adminOnlyElements.forEach(el => el.style.display = 'flex');
        } else {
            if (addBtn) addBtn.style.display = 'none';
            if (loginBtn) loginBtn.style.display = 'block';
            if (logoutBtn) logoutBtn.style.display = 'none';
            adminOnlyElements.forEach(el => el.style.display = 'none');
        }
    }

    bindEvents() {
        // 添加书签按钮
        const addBtn = document.getElementById('add-bookmark-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showAddModal());
        }

        // 登出按钮
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // 模态框控制
        const closeModal = document.getElementById('close-modal');
        if (closeModal) {
            closeModal.addEventListener('click', () => this.hideModal());
        }

        const cancelBtn = document.getElementById('cancel-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hideModal());
        }

        // 表单提交
        const bookmarkForm = document.getElementById('bookmark-form');
        if (bookmarkForm) {
            bookmarkForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // 编辑和删除按钮
        this.bindItemEvents();

        // 删除确认模态框
        const cancelDelete = document.getElementById('cancel-delete');
        if (cancelDelete) {
            cancelDelete.addEventListener('click', () => this.hideDeleteModal());
        }

        const confirmDelete = document.getElementById('confirm-delete');
        if (confirmDelete) {
            confirmDelete.addEventListener('click', () => this.confirmDelete());
        }

        // 点击模态框外部关闭
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('bookmark-modal');
            const deleteModal = document.getElementById('delete-modal');
            if (e.target === modal) {
                this.hideModal();
            }
            if (e.target === deleteModal) {
                this.hideDeleteModal();
            }
        });
    }

    bindItemEvents() {
        // 编辑按钮
        document.querySelectorAll('.edit-bookmark').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.target.dataset.id);
                this.showEditModal(id);
            });
        });

        // 删除按钮
        document.querySelectorAll('.delete-bookmark').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.target.dataset.id);
                this.showDeleteModal(id);
            });
        });
    }

    setupSearchAndFilter() {
        // 搜索功能
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.filterBookmarks(e.target.value);
                }, 300);
            });
        }
    }

    showAddModal() {
        if (!this.isAdmin) {
            this.showMessage('需要管理员权限', 'error');
            return;
        }
        document.getElementById('modal-title').textContent = '添加书签';
        document.getElementById('bookmark-form').reset();
        document.getElementById('bookmark-id').value = '';
        this.currentBookmarkId = null;
        this.showModal();
    }

    showEditModal(bookmarkId) {
        if (!this.isAdmin) {
            this.showMessage('需要管理员权限', 'error');
            return;
        }
        this.currentBookmarkId = bookmarkId;
        document.getElementById('modal-title').textContent = '编辑书签';
        
        // 从页面中获取书签数据
        const bookmarkItem = document.querySelector(`.bookmark-item[data-id="${bookmarkId}"]`);
        if (bookmarkItem) {
            const title = bookmarkItem.querySelector('.bookmark-title a').textContent.trim(); // 清理空白字符
            const url = bookmarkItem.querySelector('.bookmark-title a').href;
            const tags = Array.from(bookmarkItem.querySelectorAll('.tag')).map(tag => tag.textContent.trim()); // 清理标签空白

            // 填充表单
            document.getElementById('bookmark-id').value = bookmarkId;
            document.getElementById('bookmark-title').value = title;
            document.getElementById('bookmark-url').value = url;
            document.getElementById('bookmark-tags').value = tags.join(', ');
        }

        this.showModal();
    }

    showDeleteModal(bookmarkId) {
        if (!this.isAdmin) {
            this.showMessage('需要管理员权限', 'error');
            return;
        }
        this.currentBookmarkId = bookmarkId;
        document.getElementById('delete-modal').style.display = 'flex';
    }

    async handleLogout() {
        try {
            const response = await fetch('/admin/logout');
            if (response.ok) {
                this.showMessage('已退出登录', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        } catch (error) {
            console.error('Logout error:', error);
            this.showMessage('退出失败', 'error');
        }
    }

    hideDeleteModal() {
        document.getElementById('delete-modal').style.display = 'none';
        this.currentBookmarkId = null;
    }

    showModal() {
        document.getElementById('bookmark-modal').style.display = 'flex';
    }

    hideModal() {
        document.getElementById('bookmark-modal').style.display = 'none';
        this.currentBookmarkId = null;
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = {
            title: document.getElementById('bookmark-title').value.trim(),
            url: document.getElementById('bookmark-url').value.trim(),
            description: '',
            tags: document.getElementById('bookmark-tags').value
                .split(',')
                .map(tag => tag.trim())
                .filter(tag => tag.length > 0)
        };

        // 验证必填字段
        if (!formData.title || !formData.url) {
            this.showMessage('标题和网址为必填项', 'error');
            return;
        }

        try {
            let response;
            if (this.currentBookmarkId) {
                // 更新书签
                response = await fetch(`/api/bookmarks/${this.currentBookmarkId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
            } else {
                // 添加新书签
                response = await fetch('/api/bookmarks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
            }

            const result = await response.json();
            
            if (result.success) {
                this.showMessage(
                    this.currentBookmarkId ? '书签更新成功' : '书签添加成功',
                    'success'
                );
                this.hideModal();
                // 刷新页面以显示更新后的数据
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                this.showMessage(result.error || '操作失败', 'error');
                // 如果是权限错误，刷新页面状态
                if (response.status === 401) {
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                }
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('网络错误，请稍后重试', 'error');
        }
    }

    async confirmDelete() {
        if (!this.currentBookmarkId) return;

        try {
            const response = await fetch(`/api/bookmarks/${this.currentBookmarkId}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showMessage('书签删除成功', 'success');
                this.hideDeleteModal();
                
                // 从DOM中移除书签项
                const bookmarkItem = document.querySelector(`.bookmark-item[data-id="${this.currentBookmarkId}"]`);
                if (bookmarkItem) {
                    // 添加删除动画类
                    bookmarkItem.classList.add('deleting');
                    
                    // 动画完成后移除元素
                    setTimeout(() => {
                        bookmarkItem.remove();
                        
                        // 检查是否还有书签，如果没有则显示空状态
                        this.updateEmptyState();
                    }, 300);
                } else {
                    console.warn(`Bookmark item with id ${this.currentBookmarkId} not found in DOM`);
                    // 如果找不到元素，刷新页面以确保数据一致性
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
                
                // 重置当前书签ID
                this.currentBookmarkId = null;
            } else {
                this.showMessage(result.error || '删除失败', 'error');
                // 如果是权限错误，刷新页面状态
                if (response.status === 401) {
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                }
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('网络错误，请稍后重试', 'error');
        }
    }

    filterBookmarks(query) {
        const bookmarkItems = document.querySelectorAll('.bookmark-item');
        
        if (!query.trim()) {
            // 显示所有书签
            bookmarkItems.forEach(item => item.style.display = 'block');
            return;
        }

        const lowerQuery = query.toLowerCase();
        
        bookmarkItems.forEach(item => {
            const title = item.querySelector('.bookmark-title').textContent.trim().toLowerCase(); // 清理空白字符
            const tags = Array.from(item.querySelectorAll('.tag'))
                .map(tag => tag.textContent.trim().toLowerCase()) // 清理标签空白
                .join(' ');
            
            const matches = title.includes(lowerQuery) || 
                          tags.includes(lowerQuery);
            
            item.style.display = matches ? 'block' : 'none';
        });
    }

    updateEmptyState() {
        const bookmarkGrid = document.querySelector('.bookmark-grid');
        const emptyState = document.querySelector('.empty-state');
        const bookmarkContainer = document.querySelector('.bookmark-container');
        
        if (bookmarkGrid && bookmarkContainer) {
            const remainingBookmarks = bookmarkGrid.querySelectorAll('.bookmark-item');
            
            if (remainingBookmarks.length === 0) {
                // 移除书签网格
                bookmarkGrid.remove();
                
                // 显示空状态
                if (!emptyState) {
                    const emptyDiv = document.createElement('div');
                    emptyDiv.className = 'empty-state';
                    emptyDiv.innerHTML = '<p>还没有书签，点击"添加书签"开始收藏吧！</p>';
                    bookmarkContainer.appendChild(emptyDiv);
                }
            }
        }
    }

    showMessage(message, type = 'info') {
        // 创建消息提示
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;
        
        // 添加样式
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        // 根据类型设置背景色
        switch (type) {
            case 'success':
                messageDiv.style.backgroundColor = '#28a745';
                break;
            case 'error':
                messageDiv.style.backgroundColor = '#dc3545';
                break;
            default:
                messageDiv.style.backgroundColor = '#17a2b8';
        }

        // 添加动画
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);

        document.body.appendChild(messageDiv);

        // 3秒后自动移除
        setTimeout(() => {
            messageDiv.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 3000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new BookmarkManager();
});