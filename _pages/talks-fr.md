---
layout: archive
permalink: /fr/talks/
author_profile: true
lang: fr
locale: fr-FR
nav_key: fr
translations:
  en: /en/talks/
  fr: /fr/talks/
---

<section class="page__content" itemprop="text" markdown="1">

{% if site.talkmap_link == true %}

<p style="text-decoration:underline;"><a href="/fr/talkmap/">Voir une carte de tous les lieux où j'ai présenté une communication.</a></p>

{% endif %}

## Communications

{% assign talks_items = site.data.generated_talks | where: "section", "talks" | sort: "sort_key" | reverse %}
{% for item in talks_items %}
  {% include archive-single-talk.html item=item %}
{% endfor %}

## Posters

{% assign poster_items = site.data.generated_talks | where: "section", "posters" | sort: "sort_key" | reverse %}
{% for item in poster_items %}
  {% include archive-single-talk.html item=item %}
{% endfor %}

</section>