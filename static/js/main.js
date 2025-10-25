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
                showImagePreview(img.src, img.alt);
            });
        });
    }

    /**
     * 显示图片预览模态框
     */
    function showImagePreview(imageUrl, altText = '') {
        let currentScale = 1;
        const scaleStep = 0.2;
        const minScale = 0.5;
        const maxScale = 3;
        
        // 拖动相关变量 - 只允许Y轴拖动
        let isDragging = false;
        let startY = 0;
        let translateY = 0;
        
        // 获取文章内容区域的宽度
        const articleMain = document.querySelector('.c-article__main');
        const articleWidth = articleMain ? articleMain.offsetWidth : 800; // 默认800px
        
        // 创建遮罩层
        const overlay = document.createElement('div');
        overlay.className = 'image-preview-overlay';
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
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
            overflow: hidden;
        `;
        
        // 创建图片容器（用于居中和缩放）
        const imageContainer = document.createElement('div');
        imageContainer.style.cssText = `
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            width: ${articleWidth}px;
            max-width: 90%;
            height: 100%;
            cursor: grab;
        `;
        
        // 创建加载指示器
        const loader = document.createElement('div');
        loader.className = 'image-loader';
        loader.style.cssText = `
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        `;
        
        imageContainer.appendChild(loader);
        overlay.appendChild(imageContainer);
        document.body.appendChild(overlay);
        
        // 触发淡入动画
        setTimeout(() => {
            overlay.style.opacity = '1';
        }, 10);
        
        // 预加载图片
        const img = new Image();
        
        img.onload = function() {
            // 移除加载指示器
            loader.remove();
            
            // 创建放大的图片
            const zoomedImg = document.createElement('img');
            zoomedImg.src = imageUrl;
            zoomedImg.alt = altText;
            zoomedImg.style.cssText = `
                width: 100%;
                height: auto;
                object-fit: contain;
                opacity: 0;
                transition: opacity 0.3s ease;
                transform: scale(1) translateY(0px);
                cursor: grab;
                user-select: none;
                pointer-events: auto;
            `;
            
            imageContainer.appendChild(zoomedImg);
            
            // 触发图片淡入
            setTimeout(() => {
                zoomedImg.style.opacity = '1';
            }, 10);
            
            // 更新变换 - 只使用Y轴平移
            function updateTransform() {
                zoomedImg.style.transform = `scale(${currentScale}) translateY(${translateY}px)`;
            }
            
            // 鼠标拖动事件 - 只处理Y轴
            zoomedImg.addEventListener('mousedown', (e) => {
                isDragging = true;
                startY = e.clientY - translateY;
                zoomedImg.style.cursor = 'grabbing';
                imageContainer.style.cursor = 'grabbing';
                e.preventDefault();
            });
            
            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                translateY = e.clientY - startY;
                updateTransform();
            });
            
            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    zoomedImg.style.cursor = 'grab';
                    imageContainer.style.cursor = 'grab';
                }
            });
            
            // 触摸拖动事件（移动端）- 只处理Y轴
            zoomedImg.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    isDragging = true;
                    const touch = e.touches[0];
                    startY = touch.clientY - translateY;
                    e.preventDefault();
                }
            }, { passive: false });
            
            document.addEventListener('touchmove', (e) => {
                if (!isDragging || e.touches.length !== 1) return;
                const touch = e.touches[0];
                translateY = touch.clientY - startY;
                updateTransform();
            }, { passive: false });
            
            document.addEventListener('touchend', () => {
                isDragging = false;
            });
            
            // 鼠标滚轮缩放
            imageContainer.addEventListener('wheel', (e) => {
                e.preventDefault();
                const delta = e.deltaY > 0 ? -scaleStep : scaleStep;
                const newScale = currentScale + delta;
                
                if (newScale >= minScale && newScale <= maxScale) {
                    currentScale = newScale;
                    updateTransform();
                    updateScaleDisplay();
                }
            }, { passive: false });
            
            // 创建控制按钮容器
            const controls = document.createElement('div');
            controls.className = 'image-preview-controls';
            controls.style.cssText = `
                position: fixed;
                bottom: 40px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 10px;
                background: rgba(0,0,0,0.7);
                padding: 10px 20px;
                border-radius: 30px;
                backdrop-filter: blur(10px);
                z-index: 10001;
            `;
            
            // 创建缩放按钮样式
            const buttonStyle = `
                width: 40px;
                height: 40px;
                border: none;
                background: rgba(255,255,255,0.2);
                color: white;
                border-radius: 50%;
                cursor: pointer;
                font-size: 20px;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
                user-select: none;
            `;
            
            // 放大按钮
            const zoomInBtn = document.createElement('button');
            zoomInBtn.innerHTML = '+';
            zoomInBtn.title = '放大';
            zoomInBtn.style.cssText = buttonStyle;
            zoomInBtn.addEventListener('mouseenter', () => {
                zoomInBtn.style.background = 'rgba(255,255,255,0.3)';
                zoomInBtn.style.transform = 'scale(1.1)';
            });
            zoomInBtn.addEventListener('mouseleave', () => {
                zoomInBtn.style.background = 'rgba(255,255,255,0.2)';
                zoomInBtn.style.transform = 'scale(1)';
            });
            zoomInBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (currentScale < maxScale) {
                    currentScale += scaleStep;
                    updateTransform();
                    updateScaleDisplay();
                }
            });
            
            // 缩小按钮
            const zoomOutBtn = document.createElement('button');
            zoomOutBtn.innerHTML = '−';
            zoomOutBtn.title = '缩小';
            zoomOutBtn.style.cssText = buttonStyle;
            zoomOutBtn.addEventListener('mouseenter', () => {
                zoomOutBtn.style.background = 'rgba(255,255,255,0.3)';
                zoomOutBtn.style.transform = 'scale(1.1)';
            });
            zoomOutBtn.addEventListener('mouseleave', () => {
                zoomOutBtn.style.background = 'rgba(255,255,255,0.2)';
                zoomOutBtn.style.transform = 'scale(1)';
            });
            zoomOutBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (currentScale > minScale) {
                    currentScale -= scaleStep;
                    updateTransform();
                    updateScaleDisplay();
                }
            });
            
            // 重置按钮
            const resetBtn = document.createElement('button');
            resetBtn.innerHTML = '↻';
            resetBtn.title = '重置';
            resetBtn.style.cssText = buttonStyle;
            resetBtn.addEventListener('mouseenter', () => {
                resetBtn.style.background = 'rgba(255,255,255,0.3)';
                resetBtn.style.transform = 'scale(1.1)';
            });
            resetBtn.addEventListener('mouseleave', () => {
                resetBtn.style.background = 'rgba(255,255,255,0.2)';
                resetBtn.style.transform = 'scale(1)';
            });
            resetBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                currentScale = 1;
                translateY = 0;
                updateTransform();
                updateScaleDisplay();
            });
            
            // 缩放比例显示
            const scaleDisplay = document.createElement('div');
            scaleDisplay.style.cssText = `
                color: white;
                font-size: 14px;
                padding: 0 10px;
                display: flex;
                align-items: center;
                min-width: 50px;
                justify-content: center;
                user-select: none;
            `;
            scaleDisplay.textContent = '100%';
            
            function updateScaleDisplay() {
                scaleDisplay.textContent = Math.round(currentScale * 100) + '%';
            }
            
            // 关闭按钮
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '×';
            closeBtn.title = '关闭 (ESC)';
            closeBtn.style.cssText = buttonStyle + 'font-size: 28px;';
            closeBtn.addEventListener('mouseenter', () => {
                closeBtn.style.background = 'rgba(255,100,100,0.5)';
                closeBtn.style.transform = 'scale(1.1)';
            });
            closeBtn.addEventListener('mouseleave', () => {
                closeBtn.style.background = 'rgba(255,255,255,0.2)';
                closeBtn.style.transform = 'scale(1)';
            });
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closePreview();
            });
            
            // 组装控制按钮
            controls.appendChild(zoomOutBtn);
            controls.appendChild(scaleDisplay);
            controls.appendChild(zoomInBtn);
            controls.appendChild(resetBtn);
            controls.appendChild(closeBtn);
            
            overlay.appendChild(controls);
            
            // 阻止控制按钮容器的点击事件冒泡
            controls.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        };
        
        img.onerror = function() {
            // 移除加载指示器
            loader.remove();
            
            // 显示错误信息
            const errorMsg = document.createElement('div');
            errorMsg.style.cssText = `
                color: white;
                font-size: 18px;
                text-align: center;
                padding: 20px;
            `;
            errorMsg.textContent = '图片加载失败';
            imageContainer.appendChild(errorMsg);
        };
        
        // 开始加载图片
        img.src = imageUrl;
        
        // 点击遮罩层关闭（但不包括拖动后的点击）
        let clickStartTime = 0;
        let clickStartY = 0;
        
        overlay.addEventListener('mousedown', (e) => {
            clickStartTime = Date.now();
            clickStartY = e.clientY;
        });
        
        overlay.addEventListener('click', function(e) {
            // 只有在快速点击且没有移动太多时才关闭
            const timeDiff = Date.now() - clickStartTime;
            const distance = Math.abs(e.clientY - clickStartY);
            
            if (e.target === overlay && timeDiff < 300 && distance < 10) {
                closePreview();
            }
        });
        
        // ESC键关闭
        function handleEsc(e) {
            if (e.key === 'Escape') {
                closePreview();
                document.removeEventListener('keydown', handleEsc);
            }
        }
        document.addEventListener('keydown', handleEsc);
        
        // 关闭预览函数
        function closePreview() {
            overlay.style.opacity = '0';
            setTimeout(() => {
                if (overlay.parentNode) {
                    document.body.removeChild(overlay);
                }
            }, 300);
        }
    }

    /**
     * 处理超链接点击 - 区分图片链接和普通链接
     */
    function handleImageLinks() {
        // 图片文件扩展名正则
        const imageExtensions = /\.(png|jpe?g|gif|webp|bmp|svg)$/i;
        
        // 监听所有文章内容区域的链接点击
        document.addEventListener('click', function(e) {
            // 查找最近的 <a> 标签
            const link = e.target.closest('a');
            
            // 如果不是链接或没有 href，直接返回
            if (!link || !link.href) return;
            
            // 检查链接是否在文章内容区域（包括引用块）
            const articleMain = link.closest('.c-article__main');
            if (!articleMain) return;
            
            // 检查是否是图片链接
            if (imageExtensions.test(link.href)) {
                e.preventDefault();
                e.stopPropagation();
                
                // 获取链接文本作为 alt
                const altText = link.textContent || link.title || '';
                showImagePreview(link.href, altText);
            }
            // 非图片链接保持默认行为（正常跳转）
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
            fastScrollTo(0);
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
        
        // 使用更快的自定义滚动动画
        fastScrollTo(targetPosition);
    }
    
    /**
     * 快速滚动到指定位置
     */
    function fastScrollTo(targetPosition) {
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        const duration = Math.min(400, Math.abs(distance) * 0.8); // 更快的滚动，最长400ms
        const startTime = performance.now();
        
        const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4); // 更快的缓动函数
        
        const scrollStep = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = easeOutQuart(progress);
            
            window.scrollTo(0, startPosition + distance * easedProgress);
            
            if (progress < 1) {
                requestAnimationFrame(scrollStep);
            }
        };
        
        requestAnimationFrame(scrollStep);
    }

    /**
     * 初始化所有功能
     */
    function init() {
        addCodeCopyButtons();
        addImageZoom();
        addBackToTop();
        handleAnchorScrolling();
        handleImageLinks();
        addSpinnerAnimation();
    }

    /**
     * 添加加载动画的CSS
     */
    function addSpinnerAnimation() {
        // 检查是否已存在动画样式
        if (document.getElementById('spinner-animation-style')) return;
        
        const style = document.createElement('style');
        style.id = 'spinner-animation-style';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* 防止body滚动 */
            body.image-preview-open {
                overflow: hidden;
            }
        `;
        document.head.appendChild(style);
    }

    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();