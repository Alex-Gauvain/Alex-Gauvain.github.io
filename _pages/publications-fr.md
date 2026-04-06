---
layout: archive
title: ""
permalink: /fr/publications/
author_profile: true
lang: fr
locale: fr-FR
nav_key: fr
translations:
  en: /en/publications/
  fr: /fr/publications/
---

<section class="page__content" itemprop="text" markdown="1">

{% if site.author.googlescholar %}
  <div class="wordwrap">Vous pouvez également retrouver mes articles sur <a href="{{site.author.googlescholar}}">mon profil Google Scholar</a>.</div>
{% endif %}

{% include base_path %}

{% assign publication_items = site.data.generated_publications | where_exp: "item", "item.category != 'conferences'" %}
{% assign publication_items = publication_items | where_exp: "item", "item.year_label != 'in prep.'" | sort: "sort_key" | reverse %}

## Articles et prépublications

{% for item in publication_items %}
  {% if item.category == 'manuscripts' %}
    {% include archive-single.html item=item %}
  {% endif %}
{% endfor %}

## Rapports

{% for item in publication_items %}
  {% if item.category == 'reports' %}
    {% include archive-single.html item=item %}
  {% endif %}
{% endfor %}

## Thèses et mémoires

{% for item in publication_items %}
  {% if item.category == 'theses' %}
    {% include archive-single.html item=item %}
  {% endif %}
{% endfor %}

</section>