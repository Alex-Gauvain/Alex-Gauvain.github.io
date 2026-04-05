---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

Profile
======
Postdoctoral researcher in hydrology and hydrogeology working on groundwater modelling, climate-change impacts on water resources, and planetary hydrology for early Mars. My work combines field observations, geospatial data, reproducible numerical modelling, and research software development.

Current appointment
======
* **2022-present** - Postdoctoral researcher, Laboratoire de Meteorologie Dynamique, CNRS / IPSL / Sorbonne Universite, Paris, France.
  Development of a global hydrological model for early Mars within the ERC Mars Through Time project.

Research interests
======
* Groundwater and hydrological modelling across scales, from hillslopes and catchments to planetary hydrology.
* Multi-source calibration using field observations, tracers, stream networks and geospatial data.
* Groundwater transit times, recharge dynamics, groundwater-surface water interactions and climate-change impacts on water resources.
* Reproducible modelling workflows and open research software.

Education
======
* **2022** - PhD in Earth and Environmental Sciences, Universite de Rennes 1 / Geosciences Rennes.
* **2016** - MSc in Earth and Environmental Sciences (Hydro3), Universite de Rennes 1.
* **2014** - Bachelor's degree in Environmental Treatment and Valorisation Processes, Universite Bretagne Sud.
* **2013** - DUT in Health, Safety and Environment, Universite Bretagne Sud.

Professional experience
======
* **2022** - Research engineer in hydrogeological modelling, Geosophy, Paris, France.
* **2017-2019** - Research engineer in hydrogeology, Geosciences Rennes / OSUR, Rennes, France.

Teaching and supervision
======
* GIS practical sessions in the Master's programme in Water Sciences at the University of Rennes.
* Field supervision in Normandy and Brittany for Master students.
* HydroModPy training for interns, PhD students and postdoctoral researchers.
* Supervision of research internships in Mars hydrology, reconstructed palaeotopography and hydrogeological modelling tools.

Research software and computing
======
* HydroModPy - open-source Python toolbox for catchment-scale shallow groundwater models.
* PEM - hydrological component of the Planetary Evolution Model for early Mars.
* Main languages and environments: Python, Fortran, Bash, C++, R, Matlab, Linux, Git, QGIS/ArcGIS, MODFLOW, MODPATH, MT3DMS.

Selected talks and presentations
======
* **2025** - Constraining Early Mars Climate Through Coupled Hydrological Modeling and Comparison with Geomorphological Evidence, EPSC-DPS 2025 and Mars Through Time conference.
* **2024** - A Global High-Resolution Hydrological Model: Conceptual Study of the Distribution of Surface Water Reservoirs on Early Mars, Tenth International Conference on Mars.
* **2023** - HydroModPy: Une application python pour automatiser le deploiement des modeles de bassin versant a grande echelle, Reunion des sciences de la Terre.

Service and community
======
* Reviewer for *Hydrogeology Journal* and *Geoscientific Model Development*.
* Organisation and animation of HydroModPy development workshops and collective coding sessions.
* Scientific dissemination through CNRS outreach material, stakeholder-oriented transfer in RIVAGES Normands 2100, and science communication media.

Publications
======
{% assign publication_items = site.data.generated_publications | sort: "sort_key" | reverse %}
<ul>{% for item in publication_items %}
  {% include archive-single-cv.html item=item %}
{% endfor %}</ul>
