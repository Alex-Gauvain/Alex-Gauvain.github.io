{% include_relative includes/programs-style.html %}

{% assign sorted_publications = site.data.generated_publications | sort: "sort_key" | reverse %}
{% assign sorted_talks = site.data.generated_talks | sort: "sort_key" | reverse %}

<div class="program-intro">
Cette page rassemble les deux principaux programmes de modélisation qui structurent mon travail actuel : HydroModPy pour la modélisation des nappes à l'échelle du bassin versant, et un modèle hydrologique global haute résolution destiné à explorer la dynamique des eaux de surface sur Mars primitive.
</div>

<div class="program-list">
  <section class="program-card">
    <div class="program-card__header">
      <p class="program-card__eyebrow">Logiciel de recherche</p>
      <h2>HydroModPy</h2>
      <p class="program-card__lead">Une boîte à outils Python open-source pour déployer, calibrer et analyser des modèles de nappes peu profondes à l'échelle du bassin versant.</p>
    </div>

    <div class="program-card__content">
      <div>
        <p>HydroModPy a été développé pour standardiser la mise en place de modèles hydrogéologiques sur plusieurs bassins, à partir de modèles numériques de terrain et de jeux de données complémentaires comme l'hydrographie, la piézométrie ou la géologie.</p>

        <ul class="program-points">
          <li>Automatise l'extraction des bassins, la discrétisation et l'assemblage des données depuis les échelles locales jusqu'aux bases nationales.</li>
          <li>Construit des flux de travail reproductibles autour de Python, FloPy, Whitebox et de solveurs comme MODFLOW et MODPATH.</li>
          <li>Facilite le déploiement multi-sites, l'analyse comparative, les stratégies de calibration et les usages pédagogiques.</li>
        </ul>

        <div class="program-actions">
          <a class="btn" href="https://github.com/HydroModPy/HydroModPy">Dépôt GitHub</a>
          <a class="btn btn--inverse" href="https://hydromodpy-docs.readthedocs.io/en/latest/">Documentation</a>
        </div>
      </div>

      <aside class="program-side">
        <img class="program-side__logo" src="{{ '/images/hydromodpy-logo-long.png' | relative_url }}" alt="Logo HydroModPy">
        <h3>Périmètre</h3>
        <ul>
          <li>Boîte à outils Python</li>
          <li>Nappes peu profondes à l'échelle du bassin</li>
          <li>Déploiement multi-sites</li>
          <li>Recherche et enseignement</li>
        </ul>
      </aside>
    </div>

    <div class="program-related">
      <h3>Publication liée</h3>
      {% assign hydromodpy_pub_rendered = false %}
      {% for item in sorted_publications %}
        {% if hydromodpy_pub_rendered %}{% break %}{% endif %}
        {% if item.category == 'manuscripts' and item.title contains 'HydroModPy' and item.link != blank %}
          {% include archive-single.html item=item %}
          {% assign hydromodpy_pub_rendered = true %}
        {% endif %}
      {% endfor %}

      <h3>Communications</h3>
      {% assign hydromodpy_talk_count = 0 %}
      {% for item in sorted_talks %}
        {% if hydromodpy_talk_count >= 2 %}{% break %}{% endif %}
        {% if item.title contains 'HydroModPy' %}
          {% include archive-single-talk.html item=item %}
          {% assign hydromodpy_talk_count = hydromodpy_talk_count | plus: 1 %}
        {% endif %}
      {% endfor %}
    </div>
  </section>

  <section class="program-card">
    <div class="program-card__header">
      <p class="program-card__eyebrow">Hydrologie planétaire</p>
      <h2>Modèle hydrologique global pour Mars primitive</h2>
      <p class="program-card__lead">Un cadre de modélisation à l'échelle kilométrique conçu pour simuler la distribution, le remplissage et les débordements des réservoirs liquides de surface sur Mars primitive.</p>
    </div>

    <div class="program-card__content">
      <div>
        <p>Ce modèle exploite la topographie MOLA pour construire une base hydrologique globale des dépressions, des points de débordement, des connexions entre bassins et des relations élévation-volume-surface des lacs. Il sert à tester des scénarios climatiques à partir des indices géomorphologiques.</p>

        <ul class="program-points">
          <li>Suit les transferts d'eau entre bassins en fonction des capacités de stockage et des chemins de débordement.</li>
          <li>Simule la formation ou l'assèchement de lacs et d'océans selon les hypothèses de précipitation, d'évaporation et de couche d'eau globale équivalente.</li>
          <li>Compare les patrons d'eau de surface simulés aux lacs ouverts ou fermés, aux deltas et aux réseaux de vallées observés sur Mars.</li>
        </ul>

        <div class="program-actions">
          <a class="btn" href="{{ '/fr/publications/' | relative_url }}">Publications</a>
          <a class="btn btn--inverse" href="{{ '/fr/talks/' | relative_url }}">Communications</a>
        </div>
      </div>

      <aside class="program-side">
        <img src="{{ '/files/mars.gif' | relative_url }}" alt="Animation du modèle hydrologique global sur Mars">
        <h3>Focales actuelles</h3>
        <ul>
          <li>Hydrologie de surface à l'échelle planétaire</li>
          <li>Topographie MOLA haute résolution</li>
          <li>Lacs, océans et chemins de débordement</li>
          <li>Contraintes climatiques et géomorphologiques</li>
        </ul>
      </aside>
    </div>

    <div class="program-related">
      <h3>Publication liée</h3>
      {% assign mars_pub_rendered = false %}
      {% for item in sorted_publications %}
        {% if mars_pub_rendered %}{% break %}{% endif %}
        {% if item.category == 'manuscripts' and item.title contains 'Mars' and item.title contains 'Hydrological' and item.link != blank %}
          {% include archive-single.html item=item %}
          {% assign mars_pub_rendered = true %}
        {% endif %}
      {% endfor %}

      <h3>Communications et posters</h3>
      {% assign mars_talk_count = 0 %}
      {% for item in sorted_talks %}
        {% if mars_talk_count >= 4 %}{% break %}{% endif %}
        {% if item.title contains 'Mars' and item.title contains 'Hydrological' %}
          {% include archive-single-talk.html item=item %}
          {% assign mars_talk_count = mars_talk_count | plus: 1 %}
        {% endif %}
      {% endfor %}
    </div>
  </section>
</div>