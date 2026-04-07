{% include programs-style.html %}

{% assign sorted_publications = site.data.generated_publications | sort: "sort_key" | reverse %}
{% assign sorted_talks = site.data.generated_talks | sort: "sort_key" | reverse %}

<div class="program-list">
  <section class="program-card">
    <div class="program-card__header">
      <p class="program-card__eyebrow">Research software</p>
      <h2>HydroModPy</h2>
      <p class="program-card__lead">An open-source Python toolbox for deploying, calibrating and analysing shallow groundwater models at catchment scale.</p>
    </div>

    <div class="program-card__content">
      <div>
        <p>HydroModPy was initiated to streamline the setup of hydrogeological models across multiple catchments, starting from digital elevation models and complementary hydrographic, piezometric or geological datasets.</p>

        <ul class="program-points">
          <li>Automates watershed extraction, discretisation and data assembly from local to national datasets.</li>
          <li>Builds reproducible workflows around Python, FloPy, Whitebox tools and groundwater solvers such as MODFLOW and MODPATH.</li>
          <li>Supports multi-site deployment, comparative analysis, calibration strategies and teaching-oriented workflows.</li>
        </ul>

        <div class="program-actions">
          <a class="btn" href="https://github.com/HydroModPy/HydroModPy">GitHub repository</a>
          <a class="btn btn--inverse" href="https://hydromodpy-docs.readthedocs.io/en/latest/">Documentation</a>
        </div>
      </div>

      <aside class="program-side">
        <img class="program-side__logo" src="{{ '/images/hydromodpy-logo-long.png' | relative_url }}" alt="HydroModPy logo">
      </aside>
    </div>

    <div class="program-related">
      <h3>Selected publication</h3>
      {% assign hydromodpy_pub_rendered = false %}
      {% for item in sorted_publications %}
        {% if hydromodpy_pub_rendered %}{% break %}{% endif %}
        {% if item.category == 'manuscripts' and item.title contains 'HydroModPy' and item.link != blank %}
          {% include archive-single.html item=item %}
          {% assign hydromodpy_pub_rendered = true %}
        {% endif %}
      {% endfor %}

      <h3>Talks</h3>
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
      <p class="program-card__eyebrow">Planetary hydrology</p>
      <h2>Global Hydrological Model for Early Mars</h2>
      <p class="program-card__lead">A km-scale modelling framework designed to simulate the distribution, filling and overspill of liquid surface reservoirs on early Mars.</p>
    </div>

    <div class="program-card__content">
      <div>
        <p>This model uses MOLA topography to build a global hydrological database of depressions, spill points, watershed connections and elevation-volume-area relationships for lakes. It is used to test climate scenarios against geomorphological evidence.</p>

        <ul class="program-points">
          <li>Tracks water transfers between watersheds according to storage capacity and spillover pathways.</li>
          <li>Simulates lake and ocean formation or drying under varying precipitation, evaporation and global equivalent water-layer assumptions.</li>
          <li>Compares modeled surface-water patterns with open and closed lakes, deltas and valley networks on Mars.</li>
        </ul>

        <div class="program-actions">
          <a class="btn" href="https://zenodo.org/records/17208793">Zenodo repository</a>
          <a class="btn btn--inverse" href="https://egusphere.copernicus.org/preprints/2025/egusphere-2025-4992/">Documentation</a>
        </div>
      </div>

      <aside class="program-side">
        <img src="{{ '/files/mars.gif' | relative_url }}" alt="Animation of the global hydrological model on Mars">
      </aside>
    </div>

    <div class="program-related">
      <h3>Selected publication</h3>
      {% assign mars_pub_rendered = false %}
      {% for item in sorted_publications %}
        {% if mars_pub_rendered %}{% break %}{% endif %}
        {% if item.category == 'manuscripts' and item.title contains 'Mars' and item.title contains 'Hydrological' and item.link != blank %}
          {% include archive-single.html item=item %}
          {% assign mars_pub_rendered = true %}
        {% endif %}
      {% endfor %}

      <h3>Selected talks and posters</h3>
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