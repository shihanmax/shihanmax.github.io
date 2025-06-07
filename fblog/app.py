from flask import Flask, render_template
import os
from datetime import datetime
import markdown
import frontmatter

app = Flask(__name__)
app.config['POSTS_DIR'] = os.path.join(os.path.dirname(__file__), '_posts')

# 文章加载函数
def load_posts():
    posts = []
    for filename in os.listdir(app.config['POSTS_DIR']):
        if filename.endswith('.md'):
            with open(os.path.join(app.config['POSTS_DIR'], filename), 'r') as f:
                post = frontmatter.load(f)
                post.metadata['date'] = datetime.strptime(post.metadata['date'], '%Y-%m-%d')
                post.metadata['content'] = markdown.markdown(post.content)
                posts.append(post.metadata)
    return sorted(posts, key=lambda x: x['date'], reverse=True)

@app.route('/')
def index():
    posts = load_posts()[:10]  # 最新10篇文章
    return render_template('index.html', posts=posts)

@app.route('/post/<path:slug>')
def show_post(slug):
    posts = [p for p in load_posts() if p['slug'] == slug]
    return render_template('post.html', post=posts[0]) if posts else 'Not Found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)