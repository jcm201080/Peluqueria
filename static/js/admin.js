// static/js/admin.js

document.addEventListener("DOMContentLoaded", function() {
    // 1. Al cargar la página, comprobamos si hay una posición guardada
    const scrollPos = sessionStorage.getItem('adminScrollPos');
    
    if (scrollPos) {
        // Si la hay, hacemos scroll automático a esa posición exacta
        window.scrollTo(0, parseInt(scrollPos));
        // Limpiamos la variable para que no afecte a futuras visitas nuevas
        sessionStorage.removeItem('adminScrollPos'); 
    }
});

// 2. Justo antes de que la página se recargue (por darle a guardar, eliminar, etc.)
window.addEventListener("beforeunload", function() {
    // Guardamos la posición actual del scroll
    sessionStorage.setItem('adminScrollPos', window.scrollY);
});