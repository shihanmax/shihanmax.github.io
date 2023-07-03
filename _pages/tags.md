---
layout: post
title: Tags
permalink: /tags/
---

<div>
{% for tag in site.tags%}
<!-- <h3 class="listing-seperator" id="{{ tag[0] }}">{{ tag[0] }}</h3> -->
    <a href="#{{ tag[0] }}"> {{ tag[0] }} ({{tag[1] | size}})</a> &nbsp; 
{% endfor %}
</div>

<hr>

<!-- <ul class="listing"> -->
{% for tag in site.tags %}
<!-- <h3 class="listing-seperator" id="{{ tag[0] }}">{{ tag[0] }}</h3> -->
<h3 id="{{ tag[0] }}">{{ tag[0] }}</h3>
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
<!-- </ul> -->