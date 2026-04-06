---
layout: archive
permalink: /en/talks/
author_profile: true
lang: en
locale: en-US
nav_key: en
translations:
  en: /en/talks/
  fr: /fr/talks/
---

<section class="page__content" itemprop="text" markdown="1">

{% if site.talkmap_link == true %}

<p style="text-decoration:underline;"><a href="/en/talkmap/">See a map of all the places I've given a talk!</a></p>

{% endif %}

## Talks

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