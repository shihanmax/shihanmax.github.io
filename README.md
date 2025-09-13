# Shihanmax's Blog

一个基于Flask的个人博客系统，完全替代Jekyll，保持原有的视觉效果和功能。

## 📁 项目结构

```
blog/
├── app.py                  # Flask应用主文件
├── requirements.txt        # Python依赖包
├── README.md              # 项目说明文档
├── 404.md                 # 404页面内容
├── CNAME                  # 域名配置
├── favicon.ico            # 网站图标
├── venv/                  # Python虚拟环境
├── logs/                  # 日志文件目录
├── _posts/                # 博客文章目录
├── _pages/                # 静态页面目录
│   ├── about.md           # 关于页面
│   └── links.md           # 友链页面
├── static/                # 静态资源
│   ├── css/
│   │   ├── main.css       # 主样式
│   │   └── highlight.css  # 代码高亮样式
│   └── js/
│       ├── main.js        # 主脚本
│       ├── theme.js       # 主题切换
│       └── fortune.js     # 随机句子
├── templates/             # HTML模板
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页模板
│   ├── post.html          # 文章详情模板
│   ├── page.html          # 页面模板
│   ├── tags.html          # 标签页模板
│   ├── timeline.html      # 时间线模板
│   └── 404.html           # 404页面模板
├── utils/                 # 工具类
│   ├── __init__.py
│   ├── post_manager.py    # 文章管理器
│   └── markdown_parser.py # Markdown解析器
├── deploy/                # 部署相关文件
│   ├── webhook.py         # GitHub Webhook服务
│   ├── start.sh           # 启动脚本
│   ├── start_webhook.sh   # Webhook启动脚本
│   ├── deploy_production.sh # 生产环境部署脚本
│   └── blog.service       # systemd服务配置
└── .jkl_bak/              # Jekyll备份文件
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Git

### 本地开发

1. 克隆项目
```bash
git clone <repository-url>
cd blog
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动应用
```bash
python app.py
```

4. 访问应用
打开浏览器访问 `http://localhost:8081`

### 使用启动脚本

```bash
# 使用启动脚本（自动创建虚拟环境、安装依赖）
./deploy/start.sh
```

## 🔧 主要功能

### 前端功能
- ✅ **响应式设计** - 支持移动端和桌面端
- ✅ **深色/浅色主题** - 支持主题切换，自动保存偏好
- ✅ **GitHub风格代码高亮** - 支持行号显示、语法高亮
- ✅ **数学公式渲染** - 支持LaTeX数学公式
- ✅ **文章标签系统** - 按标签分类文章
- ✅ **时间线视图** - 按时间顺序展示文章
- ✅ **搜索功能** - 支持文章标题和内容搜索

### 后端功能
- ✅ **Markdown解析** - 兼容Jekyll的Markdown语法
- ✅ **文章管理** - 自动读取和解析Markdown文件
- ✅ **缓存机制** - 提高页面加载速度
- ✅ **错误处理** - 友好的404页面
- ✅ **日志记录** - 详细的应用日志

### 部署功能
- ✅ **GitHub Webhook** - 支持自动部署
- ✅ **进程管理** - 自动重启应用
- ✅ **生产环境配置** - systemd服务配置

## 📝 内容管理

### 添加新文章

1. 在 `_posts/` 目录下创建Markdown文件
2. 文件名格式：`YYYY-MM-DD-title.md`
3. 文件头部添加Front Matter：

```yaml
---
title: 文章标题
date: 2024-01-01
tags: [标签1, 标签2]
categories: [分类]
description: 文章描述
---

文章内容...
```

### 图标处理

项目包含一个用于将ICO图标转换为圆角PNG图标的脚本：

```bash
# 将ICO文件转换为圆角PNG
python utils/round_corner_icon.py favicon.ico

# 指定输出文件名
python utils/round_corner_icon.py favicon.ico rounded_icon.png

# 指定圆角半径比例（0-0.5）
python utils/round_corner_icon.py favicon.ico rounded_icon.png 0.3
```

### 添加新页面

1. 在 `_pages/` 目录下创建Markdown文件
2. 文件头部添加Front Matter：

```yaml
---
title: 页面标题
layout: page
---

页面内容...
```

## 🎨 主题定制

### CSS变量

项目使用CSS变量管理主题色彩和间距：

```css
:root {
    --spacing-unit: 30px;
    --c-accent-blue: #0067FB;
    --dark-theme-background: #1a1a1a;
    --dark-theme-text: #d8d8d8;
}
```

### 字体配置

- 主字体：Inconsolata
- 代码字体：SFMono-Regular, Consolas, Liberation Mono, Menlo, Courier
- 中文字体：PingFang SC, Hiragino Sans GB, Microsoft YaHei

## 🚀 部署

### 开发环境

```bash
python app.py
```

### 生产环境

1. 配置systemd服务：
```bash
sudo cp deploy/blog.service /etc/systemd/system/
sudo systemctl enable blog
sudo systemctl start blog
```

2. 配置GitHub Webhook：
```bash
# 启动Webhook服务
./deploy/start_webhook.sh

# 在GitHub仓库设置中添加Webhook URL
# http://your-server:8082/hook
```

## 📊 技术栈

- **后端框架**：Flask
- **模板引擎**：Jinja2
- **Markdown解析**：Python-Markdown + Pygments
- **数学公式**：MathJax
- **前端框架**：原生JavaScript + CSS3
- **字体**：Inconsolata, Google Fonts

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

MIT License

## 📞 联系

- 邮箱：shihanmax@example.com
- GitHub：[shihanmax](https://github.com/shihanmax)