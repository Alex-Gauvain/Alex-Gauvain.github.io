---
layout: archive
title: "Scientific outreach"
permalink: /outreach/
author_profile: true
---

{% include base_path %}

Part of my work also involves making groundwater science visible beyond academia. The material below brings together a CNRS outreach video, a graphic report on groundwater rise along the Normandy coast, and an animation derived from coastal hydrogeological simulations.

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

<style>
.outreach-section {
    margin-top: 1.5rem;
}

.outreach-section h2,
.outreach-section h3 {
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}

.video-wrapper {
    position: relative;
    width: 100%;
    max-width: 860px;
    padding-bottom: 56.25%;
    height: 0;
    overflow: hidden;
    margin-bottom: 0.75rem;
}

.video-wrapper iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 0;
}

#viewerContainer {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 1rem 0 0.75rem;
}

#viewer {
    display: flex;
    gap: 10px;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
}

#viewer canvas {
    background: white;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.25);
    max-width: 100%;
    height: auto;
}

.navButton {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0, 0, 0, 0.55);
    color: white;
    border: none;
    font-size: 30px;
    padding: 10px 12px;
    cursor: pointer;
    transition: 0.2s ease;
    z-index: 2;
}

.navButton:hover {
    background: rgba(0, 0, 0, 0.8);
}

#prevBtn {
    left: 0;
}

#nextBtn {
    right: 0;
}

.outreach-caption {
    margin-bottom: 1.25rem;
}

.outreach-animation img {
    width: 100%;
    max-width: 900px;
    display: block;
    margin: 0 auto;
}

@media (max-width: 900px) {
    .navButton {
        font-size: 24px;
        padding: 8px 10px;
    }
}
</style>

<div class="outreach-section">
    <h2>CNRS outreach video</h2>
    <div class="video-wrapper">
        <iframe
            src="https://www.youtube.com/embed/fTFC5wVkQHY"
            title="Making groundwater visible"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen>
        </iframe>
    </div>
    <p class="outreach-caption">
        Video: <a href="https://www.youtube.com/watch?v=fTFC5wVkQHY">Making groundwater visible</a>, produced for the 80 years of CNRS.
    </p>

    <h2>Graphic report on groundwater rise</h2>
    <div id="viewerContainer">
        <button id="prevBtn" class="navButton" onclick="prevPages()">&#10094;</button>
        <div id="viewer">
            <canvas id="page1"></canvas>
            <canvas id="page2"></canvas>
        </div>
        <button id="nextBtn" class="navButton" onclick="nextPages()">&#10095;</button>
    </div>
    <p class="outreach-caption">
        Graphic report: <a href="https://grand-format.net/quand-les-nappes-montent/">Quand les nappes montent</a>, published by Grand Format.
    </p>
</div>

<script>
const pdfUrl = "{{ '/files/BD-Normandie-Nappes.pdf' | relative_url }}";
const MAX_PAGE_WIDTH = 460;

let pdfDoc = null;
let currentPage = 1;

function pagesPerView() {
    return window.innerWidth < 900 ? 1 : 2;
}

function clearCanvas(canvasId) {
    const canvas = document.getElementById(canvasId);
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = 0;
    canvas.height = 0;
}

function pageWidth() {
    const viewer = document.getElementById("viewer");
    const gap = pagesPerView() === 1 ? 0 : 10;
    const availableWidth = Math.floor((viewer.clientWidth - gap) / pagesPerView());
    return Math.max(220, Math.min(MAX_PAGE_WIDTH, availableWidth));
}

function renderPage(pageNumber, canvasId) {
    if (!pdfDoc || pageNumber > pdfDoc.numPages) {
        clearCanvas(canvasId);
        return;
    }

    pdfDoc.getPage(pageNumber).then(function(page) {
        const viewport = page.getViewport({ scale: 1 });
        const scale = pageWidth() / viewport.width;
        const scaledViewport = page.getViewport({ scale: scale });

        const canvas = document.getElementById(canvasId);
        const context = canvas.getContext("2d");

        canvas.width = scaledViewport.width;
        canvas.height = scaledViewport.height;

        page.render({
            canvasContext: context,
            viewport: scaledViewport
        });
    });
}

function renderPages() {
    const secondCanvas = document.getElementById("page2");
    renderPage(currentPage, "page1");

    if (pagesPerView() === 1) {
        secondCanvas.style.display = "none";
        clearCanvas("page2");
        return;
    }

    secondCanvas.style.display = "block";
    renderPage(currentPage + 1, "page2");
}

function nextPages() {
    const step = pagesPerView();
    if (pdfDoc && currentPage + step <= pdfDoc.numPages) {
        currentPage += step;
        renderPages();
    }
}

function prevPages() {
    const step = pagesPerView();
    if (currentPage - step >= 1) {
        currentPage -= step;
        renderPages();
    }
}

pdfjsLib.getDocument(pdfUrl).promise.then(function(pdf) {
    pdfDoc = pdf;
    renderPages();
});

window.addEventListener("resize", function() {
    if (pdfDoc) {
        renderPages();
    }
});
</script>