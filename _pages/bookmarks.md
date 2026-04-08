---
layout: page
title: Bookmarks
permalink: /bookmarks/
page_type: bookmarks
---
<article class="c-article">
  <main class="c-article__main">

    <div class="bookmark-toolbar">
      <div class="bookmark-controls">
        <input type="text" id="search-input" class="form-input" placeholder="搜索书签...">
      </div>
    </div>

    <div class="bookmark-container">
      {% assign bookmarks = site.data.bookmarks.bookmarks %}
      {% if bookmarks and bookmarks.size > 0 %}
      <div class="bookmark-grid" id="bookmark-grid">
        {% for bookmark in bookmarks %}
        <div class="bookmark-item"
             data-title="{{ bookmark.title | downcase }}"
             data-tags="{{ bookmark.tags | join: ' ' | downcase }}">
          <div class="bookmark-content">
            <div class="bookmark-main-info">
              <h4 class="bookmark-title">
                <a href="{{ bookmark.url }}" target="_blank" rel="noopener noreferrer">
                  {{ bookmark.title }}
                </a>
              </h4>
              <div class="bookmark-tags">
                {% for tag in bookmark.tags %}
                <span class="tag">{{ tag }}</span>
                {% endfor %}
              </div>
            </div>
            <div class="bookmark-meta">
              <span class="bookmark-date">{{ bookmark.created_at | slice: 0, 10 }}</span>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
      {% else %}
      <div class="empty-state">
        <p>暂无书签。</p>
      </div>
      {% endif %}
    </div>

  </main>
</article>

<script>
(function() {
    var searchInput = document.getElementById('search-input');
    var items = document.querySelectorAll('.bookmark-item');
    if (!searchInput) return;
    searchInput.addEventListener('input', function() {
        var q = this.value.trim().toLowerCase();
        items.forEach(function(item) {
            var title = item.getAttribute('data-title') || '';
            var tags = item.getAttribute('data-tags') || '';
            item.style.display = (!q || title.includes(q) || tags.includes(q)) ? '' : 'none';
        });
    });
})();
</script>
