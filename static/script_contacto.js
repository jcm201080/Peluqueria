const puebloImages = [
    "/static/img/pueblo1.jpg",
    "/static/img/pueblo2.jpg",
    "/static/img/pueblo3.jpg"
];

let contacto_index = 0;

function changeBackground() {
    const contactoSection = document.querySelector(".contacto");
    if (contactoSection) {
        contactoSection.style.backgroundImage = `url(${puebloImages[index]})`;
        contacto_index = (contacto_index + 1) % puebloImages.length;
    }
}

// Solo ejecuta si el DOM está listo
document.addEventListener("DOMContentLoaded", () => {
    changeBackground();
    setInterval(changeBackground, 5000);
});
