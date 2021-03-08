---
layout: post
title: Tags
permalink: /tags/
---

<!-- <ul class="listing"> -->
{% for tag in site.tags %}
<!-- <h3 class="listing-seperator" id="{{ tag[0] }}">{{ tag[0] }}</h3> -->
<h3>{{ tag[0] }}</h3>
{% for post in tag[1] %}
<ul style="list-style-type:circle">
    <li class="listing-item">
        <time datetime="{{ post.date | date:"%Y-%m-%d" }}">{{ post.date | date:"%Y-%m-%d" }}</time>
        <a href="{{ post.url }}" title="{{ post.title }}">{{ post.title }}</a>
    </li>
</ul>
{% endfor %}
{% endfor %}
<!-- </ul> -->