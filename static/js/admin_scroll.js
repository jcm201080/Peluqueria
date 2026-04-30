document.addEventListener("DOMContentLoaded", function() {
    // 1. Al cargar la página, comprobar si hay una posición guardada
    let scrollPos = sessionStorage.getItem('scrollPosition');
    if (scrollPos) {
        // Hacemos scroll instantáneo a esa altura
        window.scrollTo(0, parseInt(scrollPos));
        // Limpiamos la memoria para futuras visitas limpias
        sessionStorage.removeItem('scrollPosition');
    }
});

// 2. Justo antes de que la página recargue o cambie (al darle a un botón de form o enlace)
window.addEventListener("beforeunload", function() {
    // Guardamos la altura actual de la pantalla
    sessionStorage.setItem('scrollPosition', window.scrollY);
});


document.addEventListener("DOMContentLoaded", function() {
    // 1. Al cargar la página, comprobar si hay una posición guardada
    let scrollPos = sessionStorage.getItem('scrollPosition');
    if (scrollPos) {
        // Hacemos scroll instantáneo a esa altura
        window.scrollTo(0, parseInt(scrollPos));
        // Limpiamos la memoria
        sessionStorage.removeItem('scrollPosition');
    }
});

// 2. Justo antes de que la página recargue (al pulsar Anular o Reservar)
window.addEventListener("beforeunload", function() {
    // Guardamos la altura actual de la pantalla
    sessionStorage.setItem('scrollPosition', window.scrollY);
});

// static/js/admin_scroll.js

document.addEventListener("DOMContentLoaded", function() {
    // 1. Al cargar la página, comprobamos si el navegador guardó una posición previa
    let scrollPos = sessionStorage.getItem('scrollPosition');
    
    if (scrollPos) {
        // Hacemos scroll instantáneo a esa altura exacta
        window.scrollTo(0, parseInt(scrollPos));
        // Limpiamos la variable para que no afecte a futuras visitas a la página
        sessionStorage.removeItem('scrollPosition');
    }
});

// 2. Justo antes de abandonar la página (ej: al hacer clic en Anular o Reservar)
window.addEventListener("beforeunload", function() {
    // Guardamos la altura actual de la pantalla en la memoria del navegador
    sessionStorage.setItem('scrollPosition', window.scrollY);
});