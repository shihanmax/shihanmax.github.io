---
layout: post
title: Tags
permalink: /tags/
---

<div>
{% for tag in site.tags %}
    <a href="#{{ tag[0] }}"> {{ tag[0] }} ({{ tag[1] | size }})</a> &nbsp;
{% endfor %}
</div>

<hr>

{% for tag in site.tags %}
<h3 id="{{ tag[0] }}">{{ tag[0] }} <a href="#">⤴</a></h3>
{% for post in tag[1] %}
<ul style="list-style-type:circle">
    <li class="listing-item">
        <time datetime="{{ post.date | date:"%Y-%m-%d" }}">{{ post.date | date:"%Y-%m-%d" }}</time>
        <a href="{{ post.url }}" title="{{ post.title }}">{{ post.title }}</a>
    </li>
</ul>
{% endfor %}
<br/>
{% endfor %}
