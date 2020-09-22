---
layout: post
title: Timeline
permalink: /timeline/
---

<ul>
  {% for post in site.posts %}

    {% unless post.next %}
      <h2>{{ post.date | date: '%Y' }}</h2>
    {% else %}
      {% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
      {% capture nyear %}{{ post.next.date | date: '%Y' }}{% endcapture %}
      {% if year != nyear %}
      
      <h2>{{ post.date | date: '%Y' }}</h2>
      {% endif %}
    {% endunless %}

    &nbsp;{{ post.date | date:"%Y-%m-%d：" }} <a href="{{ post.url }}">{{ post.title }}</a>
    <br/>
  {% endfor %}
</ul>
