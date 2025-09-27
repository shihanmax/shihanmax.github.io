/**
 * 博客主JavaScript文件
 * 包含通用功能和交互效果
 */

(function() {
    'use strict';

    /**
     * 添加代码块复制功能
     */
    function addCodeCopyButtons() {
        const codeBlocks = document.querySelectorAll('pre code');
        
        codeBlocks.forEach(function(codeBlock) {
            const pre = codeBlock.parentNode;
            
            // 创建复制按钮
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.textContent = '复制';
            copyButton.setAttribute('aria-label', '复制代码');
            
            // 添加按钮到pre元素
            pre.style.position = 'relative';
            pre.appendChild(copyButton);
            
            // 点击复制
            copyButton.addEventListener('click', function() {
                const text = codeBlock.textContent;
                
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(function() {
                        copyButton.textContent = '已复制';
                        setTimeout(function() {
                            copyButton.textContent = '复制';
                        }, 2000);
                    });
                } else {
                    // 降级处理
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    
                    copyButton.textContent = '已复制';
                    setTimeout(function() {
                        copyButton.textContent = '复制';
                    }, 2000);
                }
            });
        });
    }

    /**
     * 添加图片点击放大功能
     */
    function addImageZoom() {
        const images = document.querySelectorAll('.c-article__main img');
        
        images.forEach(function(img) {
            img.style.cursor = 'pointer';
            
            img.addEventListener('click', function() {
                // 创建遮罩层
                const overlay = document.createElement('div');
                overlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.9);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                    cursor: pointer;
                `;
                
                // 创建放大的图片
                const zoomedImg = document.createElement('img');
                zoomedImg.src = img.src;
                zoomedImg.alt = img.alt;
                zoomedImg.style.cssText = `
                    max-width: 90%;
                    max-height: 90%;
                    object-fit: contain;
                `;
                
                overlay.appendChild(zoomedImg);
                document.body.appendChild(overlay);
                
                // 点击关闭
                overlay.addEventListener('click', function() {
                    document.body.removeChild(overlay);
                });
                
                // ESC键关闭
                function handleEsc(e) {
                    if (e.key === 'Escape') {
                        document.body.removeChild(overlay);
                        document.removeEventListener('keydown', handleEsc);
                    }
                }
                document.addEventListener('keydown', handleEsc);
            });
        });
    }

    /**
     * 添加返回顶部按钮
     */
    function addBackToTop() {
        const button = document.createElement('button');
        button.className = 'back-to-top';
        button.innerHTML = '↑';
        button.setAttribute('aria-label', '返回顶部');
        button.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--c-accent-blue);
            color: white;
            border: none;
            font-size: 20px;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 100;
        `;

        document.body.appendChild(button);

        // 显示/隐藏按钮
        function toggleButton() {
            if (window.pageYOffset > 300) {
                button.style.opacity = '1';
                button.style.visibility = 'visible';
            } else {
                button.style.opacity = '0';
                button.style.visibility = 'hidden';
            }
        }

        window.addEventListener('scroll', toggleButton);

        // 点击返回顶部
        button.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    /**
     * 处理锚点跳转，考虑固定header高度
     */
    function handleAnchorScrolling() {
        // 处理页面加载时的锚点
        if (window.location.hash) {
            setTimeout(() => {
                const target = document.querySelector(window.location.hash);
                if (target) {
                    scrollToElement(target);
                }
            }, 100);
        }
        
        // 处理点击锚点链接
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' && e.target.getAttribute('href') && e.target.getAttribute('href').startsWith('#')) {
                const targetId = e.target.getAttribute('href');
                // 确保目标ID不是空的锚点
                if (targetId && targetId.length > 1) {
                    const target = document.querySelector(targetId);
                    if (target) {
                        e.preventDefault();
                        scrollToElement(target);
                        // 更新URL
                        history.pushState(null, null, targetId);
                    }
                }
            }
        });
    }
    
    /**
     * 滚动到指定元素，考虑header高度
     */
    function scrollToElement(element) {
        // 获取header高度
        const headerHeight = parseInt(getComputedStyle(document.documentElement)
            .getPropertyValue('--header-height')) || 70;
        
        // 计算目标位置
        const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - headerHeight;
        
        // 平滑滚动
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }

    /**
     * 初始化所有功能
     */
    function init() {
        addCodeCopyButtons();
        addImageZoom();
        addBackToTop();
        handleAnchorScrolling();
    }

    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();