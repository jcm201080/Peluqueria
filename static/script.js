
const images = [
    "/static/img/fondo1.jpg",
    "/static/img/fondo2.jpg",
    "/static/img/fondo3.jpg"
];

let index = 0;

function changeHeaderBackground() {
    document.querySelector("header").style.backgroundImage = `url(${images[index]})`;
    index = (index + 1) % images.length;
}

// Cambia la imagen cada 5 segundos
setInterval(changeHeaderBackground, 5000);

// Establece la primera imagen al cargar
document.addEventListener("DOMContentLoaded", changeHeaderBackground);
