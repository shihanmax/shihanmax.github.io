---
layout: page
title: Tags
permalink: /tags/
page_type: tags
---
<section class="c-archives">
  <div class="tags-cloud">
    {% assign sorted_tags = site.tags | sort %}
    {% for tag in sorted_tags %}
      <a href="#{{ tag[0] }}" class="tag-cloud-link">{{ tag[0] }} ({{ tag[1].size }})</a> &nbsp;
    {% endfor %}
  </div>

  <hr>

  {% for tag in sorted_tags %}
  <div class="tag-section" id="{{ tag[0] }}">
    <h3>{{ tag[0] }} <a href="#">⤤</a></h3>
    {% assign tag_posts = tag[1] | sort: "date" | reverse %}
    {% for post in tag_posts %}
    <ul style="list-style-type:circle">
      <li class="listing-item">
        <time datetime="{{ post.date | date: '%Y-%m-%d' }}">{{ post.date | date: "%Y-%m-%d" }}</time>
        <a href="{{ post.url | relative_url }}" title="{{ post.title }}">{{ post.title }}</a>
      </li>
    </ul>
    {% endfor %}
    <br/>
  </div>
  {% endfor %}
</section>
