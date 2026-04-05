---
layout: archive
title: ""
permalink: /publications/
author_profile: true
---

<section class="page__content" itemprop="text" markdown="1">

{% if site.author.googlescholar %}
  <div class="wordwrap">You can also find my articles on <a href="{{site.author.googlescholar}}">my Google Scholar profile</a>.</div>
{% endif %}

{% include base_path %}

{% assign publication_items = site.data.generated_publications | where_exp: "item", "item.category != 'conferences'" %}
{% assign publication_items = publication_items | where_exp: "item", "item.year_label != 'in prep.'" | sort: "sort_key" | reverse %}

{% if site.publication_category %}
  {% for category in site.publication_category %}
    {% assign title_shown = false %}
    {% for item in publication_items %}
      {% if item.category != category[0] %}
        {% continue %}
      {% endif %}
      {% unless title_shown %}
## {{ category[1].title }}

        {% assign title_shown = true %}
      {% endunless %}
      {% include archive-single.html item=item %}
    {% endfor %}
  {% endfor %}
{% else %}
  {% for item in publication_items %}
    {% include archive-single.html item=item %}
  {% endfor %}
{% endif %}

</section>