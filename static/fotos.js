// fotos.js

document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM completamente cargado");

    const modal = document.getElementById("modal");
    const imagenAmpliada = document.getElementById("imagenAmpliada");
    const cerrar = document.getElementById("cerrar");

    if (!modal || !imagenAmpliada || !cerrar) {
        console.error("❌ Error: No se encontraron los elementos del modal.");
        return;
    }

    // Obtener todas las imágenes de la galería
    const imagenes = document.querySelectorAll(".imagen-thumb");

    console.log(`🔍 Se encontraron ${imagenes.length} imágenes.`);

    if (imagenes.length === 0) {
        console.warn("⚠️ Advertencia: No hay imágenes con la clase 'imagen-thumb'.");
        return;
    }

    // Abrir modal al hacer clic en una imagen
    imagenes.forEach(imagen => {
        imagen.addEventListener("click", function () {
            console.log(`📸 Clic en imagen: ${this.src}`);
            const fullImageUrl = this.getAttribute("data-full");

            if (!fullImageUrl) {
                console.warn("⚠️ Advertencia: La imagen no tiene el atributo data-full.");
                return;
            }

            imagenAmpliada.src = fullImageUrl;
            modal.classList.add("mostrar");
        });
    });

    // Cerrar modal al hacer clic en la "x"
    cerrar.addEventListener("click", function () {
        console.log("❌ Cerrar modal.");
        modal.classList.remove("mostrar");
    });

    // Cerrar modal si se hace clic fuera de la imagen ampliada
    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            console.log("🖱️ Clic fuera de la imagen, cerrando modal.");
            modal.classList.remove("mostrar");
        }
    });
});
