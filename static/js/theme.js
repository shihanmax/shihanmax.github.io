/**
 * 主题切换功能
 * 实现深色/浅色主题切换，保持用户偏好
 */

(function() {
    'use strict';

    // 获取DOM元素
    const toggle = document.getElementById('theme-toggle');
    const body = document.body;
    const moonIcon = document.getElementById('theme-icon-moon');
    const sunIcon = document.getElementById('theme-icon-sun');
    
    // 防抖和状态锁定
    let isToggling = false;
    let toggleTimeout = null;

    /**
     * 设置用户偏好到localStorage
     */
    function setUserPreference(preference) {
        localStorage.setItem('themePreference', preference);
    }

    /**
     * 获取用户偏好
     */
    function getUserPreference() {
        return localStorage.getItem('themePreference');
    }

    /**
     * 设置为深色主题
     */
    function setToDark() {
        const html = document.documentElement;
        
        // 更新类名 - 统一使用classList避免覆盖其他类
        html.classList.remove('light-theme');
        html.classList.add('dark-theme');
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
        
        // 设置data属性方便调试
        html.setAttribute('data-theme', 'dark');
        body.style.backgroundColor = '#1a1a1a';
        
        // 更新图标
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'block';
        
        // 更新状态
        setUserPreference('dark');
        if (toggle) toggle.checked = true;
        console.log('切换到暗色主题');
    }

    /**
     * 设置为浅色主题
     */
    function setToLight() {
        const html = document.documentElement;
        
        // 更新类名 - 统一使用classList避免覆盖其他类
        html.classList.remove('dark-theme');
        html.classList.add('light-theme');
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
        
        // 设置data属性方便调试
        html.setAttribute('data-theme', 'light');
        body.style.backgroundColor = '#f5f5f5';
        
        // 更新图标
        if (moonIcon) moonIcon.style.display = 'block';
        if (sunIcon) sunIcon.style.display = 'none';
        
        // 更新状态
        setUserPreference('light');
        if (toggle) toggle.checked = false;
        console.log('切换到亮色主题');
    }

    /**
     * 检测当前主题状态
     */
    function getCurrentTheme() {
        const savedPreference = getUserPreference();
        const html = document.documentElement;
        const htmlHasDark = html.classList.contains('dark-theme');
        const bodyHasDark = body.classList.contains('dark-theme');
        
        // 优先使用保存的偏好，否则检查DOM状态
        if (savedPreference) {
            return savedPreference;
        }
        
        // 检查HTML或Body是否有dark-theme类
        return (htmlHasDark || bodyHasDark) ? 'dark' : 'light';
    }
    
    /**
     * 同步UI状态与当前主题
     */
    function syncUIState() {
        const currentTheme = getCurrentTheme();
        const isDark = currentTheme === 'dark';
        
        console.log('同步UI状态 - 当前主题:', currentTheme);
        console.log('HTML类名:', document.documentElement.className, 'Body类名:', body.className);
        
        // 确保HTML和Body状态一致
        const html = document.documentElement;
        if (isDark) {
            html.classList.remove('light-theme');
            html.classList.add('dark-theme');
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            html.setAttribute('data-theme', 'dark');
        } else {
            html.classList.remove('dark-theme');
            html.classList.add('light-theme');
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            html.setAttribute('data-theme', 'light');
        }
        
        // 同步UI控件状态
        if (isDark) {
            if (moonIcon) moonIcon.style.display = 'none';
            if (sunIcon) sunIcon.style.display = 'block';
            if (toggle) toggle.checked = true;
        } else {
            if (moonIcon) moonIcon.style.display = 'block';
            if (sunIcon) sunIcon.style.display = 'none';
            if (toggle) toggle.checked = false;
        }
    }

    /**
     * 切换主题 - 带防抖处理
     */
    function toggleTheme() {
        // 防止快速连续点击
        if (isToggling) {
            console.log('主题切换进行中，跳过此次请求');
            return;
        }
        
        // 清除之前的延迟
        if (toggleTimeout) {
            clearTimeout(toggleTimeout);
        }
        
        isToggling = true;
        
        const currentTheme = getCurrentTheme();
        console.log('切换主题 - 当前主题:', currentTheme);
        
        // 立即执行主题切换
        if (currentTheme === 'dark') {
            setToLight();
        } else {
            setToDark();
        }
        
        // 300ms后解除锁定
        toggleTimeout = setTimeout(() => {
            isToggling = false;
            console.log('主题切换锁定解除');
        }, 300);
    }

    // 初始化
    function init() {
        if (!toggle || !moonIcon || !sunIcon) {
            console.warn('Theme toggle elements not found');
            return;
        }

        // 调试信息
        const savedPreference = getUserPreference();
        console.log('Theme.js 初始化 - 保存的主题:', savedPreference);
        console.log('HTML 类名:', document.documentElement.className);
        console.log('Body 类名:', body.className);

        // 同步UI状态（主题已在head中设置）
        syncUIState();

        // 监听主题切换 - 移除可能存在的旧监听器
        toggle.removeEventListener('change', toggleTheme);
        toggle.addEventListener('change', toggleTheme);

        // 监听系统主题变化
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                // 如果用户没有手动设置过主题，则跟随系统主题
                const currentPreference = getUserPreference();
                if (!currentPreference) {
                    if (e.matches) {
                        setToDark();
                    } else {
                        setToLight();
                    }
                }
            });
        }

        console.log('主题初始化完成');
    }

    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();