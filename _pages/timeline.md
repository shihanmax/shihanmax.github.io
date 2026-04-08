---
layout: page
title: Timeline
permalink: /timeline/
page_type: timeline
---
<article class="c-article">
  <main class="c-article__main">
    {% assign sorted_posts = site.posts | sort: "date" | reverse %}
    {% assign current_year = "" %}
    {% for post in sorted_posts %}
      {% assign post_year = post.date | date: "%Y" %}
      {% if post_year != current_year %}
        {% unless forloop.first %}</ul>{% endunless %}
        <h2>{{ post_year }}</h2>
        <ul style="list-style: none; margin-left: 0;">
        {% assign current_year = post_year %}
      {% endif %}
      <li style="margin-bottom: 0.5rem;">
        &nbsp;&nbsp;{{ post.date | date: "%Y-%m-%d" }}：
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      </li>
      {% if forloop.last %}</ul>{% endif %}
    {% endfor %}
  </main>
</article>
