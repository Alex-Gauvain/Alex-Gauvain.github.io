## Research interests

## About me

I pursued my PhD thesis (2019 - 2022) at Géosciences Rennnes from the University of Rennes (France) under the supervision of Jean-Raynald de Dreuzy (CNRS) and Luc Aquilina. The subject was about “Numerical simulation of unsaturated porous media flows by an adaptive discontinuous Galerkin method: application to sandy beaches”. The motivation is to provide a robust, efficient and accurate tool to model and compute wave-induced flows inside sandy beaches. In particular, I focused on Richards' equation to model flow dynamics in unsaturated porous media. Despite its current use, this equation is numerically challenging to solve for a wide range of cases, for instance in presence of steep wetting fronts. Moreover, at the start of my PhD, I decided to use Discontinuous Galerkin (DG) methods because of their flexibility, in particular for adaptive mesh refinement. Based on these choices, I developed a computational code called Rivage which demonstrates its abilities for such simulations through various numerical examples.

I defended my PhD thesis on the 11th Janaury 2021 in front of a jury made up of:
- Philippe Helluy, Professor, University of Strasbourg - President of the Jury
- Vít Dolejší, Professor, Charles University in Prague - Reviewer
- Philippe Ackerer, Professor, University of Strasbourg - Reviewer
- Béatrice Rivière, Professor, Rice University - Examiner
- France Floc'h, Lecturer, University of Western Brittany - Examiner
- Stéphane Bonelli, Research Director, INRAE - Invited

I was in a PostDoc for 2021 at Géosciences Montpellier laboratory from the University of Montpellier (France). I was mentored by Frédéric Bouchette. The aim was to continue my PhD work by carrying extended applications concerning large-scale experiments and real beaches. This should provide new insights and perspectives about the physics for the oceanographic/littoralist community. In addition, I am improving Rivage code for the simulation of Richards' equation by taking care more specifically of the nonlinearities and degeneracies rising at multiple space/time scales.

I am currently involved in a PostDoc at the Department of Technical Mathematics, Faculty of Mechanichal Engineering in the Czech Technical University in Prague. I am mentored by Petr Sváček. The project deals with the development of high order discontinuous Galerkin methods for numerical solution of PDEs in the continuum mechanics.



<iframe width="191" height="108"
src="https://www.youtube.com/embed/ttvEmYBBuW8">
</iframe>

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

<style>

/* CONTENEUR PRINCIPAL */
#viewerContainer {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* ZONE DES PAGES */
#viewer {
    display: flex;
    gap: 10px;
}

/* PAGES */
canvas {
    background: white;
    box-shadow: 0 0 15px rgba(0,0,0,0.6);
}

/* BOUTONS OVERLAY */
.navButton {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0,0,0,0.5);
    color: white;
    border: none;
    font-size: 30px;
    padding: 10px 10px;
    cursor: pointer;
    transition: 0.3s;
}

.navButton:hover {
    background: rgba(0,0,0,0.8);
}

#prevBtn {
    left: 0px;
}

#nextBtn {
    right: 0px;
}
</style>

<body>

<div id="viewerContainer">
    <button id="prevBtn" class="navButton" onclick="prevPages()">❮</button>

    <div id="viewer">
        <canvas id="page1"></canvas>
        <canvas id="page2"></canvas>
    </div>

    <button id="nextBtn" class="navButton" onclick="nextPages()">❯</button>
</div>

<script>
const url = "files/BD-Normandie-Nappes.pdf";
const PAGE_WIDTH = 485;

let pdfDoc = null;
let currentPage = 1;

pdfjsLib.getDocument(url).promise.then(function(pdf) {
    pdfDoc = pdf;
    renderPages();
});

function renderPage(pageNumber, canvasId) {
    pdfDoc.getPage(pageNumber).then(function(page) {

        const viewport = page.getViewport({ scale: 1 });
        const scale = PAGE_WIDTH / viewport.width;
        const scaledViewport = page.getViewport({ scale: scale });

        const canvas = document.getElementById(canvasId);
        const context = canvas.getContext("2d");

        canvas.height = scaledViewport.height;
        canvas.width = scaledViewport.width;

        page.render({
            canvasContext: context,
            viewport: scaledViewport
        });
    });
}

function renderPages() {
    renderPage(currentPage, "page1");

    if (currentPage + 1 <= pdfDoc.numPages) {
        renderPage(currentPage + 1, "page2");
    } else {
        const canvas2 = document.getElementById("page2");
        const context2 = canvas2.getContext("2d");
        context2.clearRect(0, 0, canvas2.width, canvas2.height);
    }
}

function nextPages() {
    if (currentPage + 2 <= pdfDoc.numPages) {
        currentPage += 2;
        renderPages();
    }
}

function prevPages() {
    if (currentPage - 2 >= 1) {
        currentPage -= 2;
        renderPages();
    }
}
</script>

</body>
© Grand Format


<body>
<center>
<img src="files/Breville.gif" alt="Animation GIF" style="width: 80%;">
</center>
</body>

test