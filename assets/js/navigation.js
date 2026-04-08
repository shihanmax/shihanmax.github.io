/**
 * 导航栏滚动隐藏/显示功能
 * 向下滚动时隐藏导航栏，向上滚动时显示
 */

(function() {
    'use strict';

    let lastScrollTop = 0;
    let isScrolling = false;
    let scrollTimeout = null;
    const header = document.querySelector('.c-page__header');
    const scrollThreshold = 5; // 滚动阈值，避免微小滚动触发
    const hideThreshold = 100; // 滚动超过100px才开始隐藏
    let isMobile = false; // 是否为移动端

    if (!header) {
        console.warn('Navigation header not found');
        return;
    }

    /**
     * 检测是否为移动端
     */
    function checkMobile() {
        isMobile = window.innerWidth <= 768;
    }

    /**
     * 处理滚动事件
     */
    function handleScroll() {
        // 只在移动端启用隐藏功能
        if (!isMobile) {
            showHeader();
            return;
        }
        
        // 防止频繁执行
        if (isScrolling) return;
        
        isScrolling = true;
        
        // 使用requestAnimationFrame优化性能
        window.requestAnimationFrame(() => {
            const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // 在页面顶部时始终显示导航栏
            if (currentScrollTop <= hideThreshold) {
                showHeader();
            } 
            // 向下滚动且超过阈值 - 隐藏导航栏
            else if (currentScrollTop > lastScrollTop + scrollThreshold) {
                hideHeader();
            } 
            // 向上滚动 - 显示导航栏
            else if (currentScrollTop < lastScrollTop - scrollThreshold) {
                showHeader();
            }
            
            lastScrollTop = currentScrollTop <= 0 ? 0 : currentScrollTop;
            isScrolling = false;
        });
    }

    /**
     * 隐藏导航栏
     */
    function hideHeader() {
        if (isMobile) {
            header.classList.add('header-hidden');
        }
    }

    /**
     * 显示导航栏
     */
    function showHeader() {
        header.classList.remove('header-hidden');
    }

    /**
     * 节流函数 - 限制滚动事件触发频率
     */
    function throttle(func, delay) {
        return function() {
            if (scrollTimeout) return;
            
            scrollTimeout = setTimeout(() => {
                func();
                scrollTimeout = null;
            }, delay);
        };
    }

    // 初始化
    function init() {
        // 检测是否为移动端
        checkMobile();
        
        // 确保导航栏初始状态正确
        showHeader();
        
        // 添加滚动监听器（带节流）
        window.addEventListener('scroll', throttle(handleScroll, 10));
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
            checkMobile();
            if (!isMobile) {
                showHeader();
            }
        });
        
        console.log('Navigation scroll handler initialized');
    }

    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
