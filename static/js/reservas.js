document.addEventListener('DOMContentLoaded', actualizarCalendario);

async function actualizarCalendario() {
    // 1. Verificamos cierres totales de la peluquería en la DB
    const responseBloqueados = await fetch('/api/dias-ocupados');
    const diasBloqueados = await responseBloqueados.json();

    const diasElements = document.querySelectorAll('.dia-itv');
    
    // 2. Comprobamos la disponibilidad real de cada día visible
    for (let el of diasElements) {
        const fecha = el.getAttribute('data-fecha');
        
        // Si el día entero está cerrado (festivo general)
        if (diasBloqueados.includes(fecha)) {
            marcarOcupado(el);
            continue;
        }

        // Si la peluquería está abierta, comprobamos si le quedan huecos a los peluqueros
        try {
            const responseHoras = await fetch(`/api/disponibilidad?fecha=${fecha}`);
            const horasLibres = await responseHoras.json();

            if (horasLibres.length === 0) {
                // No quedan citas libres ese día
                marcarOcupado(el);
            } else {
                // Hay huecos, lo ponemos verde
                marcarDisponible(el);
            }
        } catch (error) {
            console.error("Error consultando disponibilidad:", error);
            marcarOcupado(el); // Por seguridad, si falla la conexión lo marcamos bloqueado
        }
    }
}

function marcarOcupado(elemento) {
    elemento.classList.add('ocupado');
    elemento.classList.remove('disponible');
    elemento.onclick = null; // Desactiva el clic por completo
}

function marcarDisponible(elemento) {
    elemento.classList.add('disponible');
    elemento.classList.remove('ocupado');
}

// Esta función es llamada directamente por el 'onclick' del HTML
window.seleccionarDia = function(elemento, fecha) {
    // Evitar hacer clic en un día rojo (ocupado)
    if (elemento.classList.contains('ocupado')) return;
    
    // Quitar la clase 'active' de todos los días y ponérsela al actual
    document.querySelectorAll('.dia-itv').forEach(d => d.classList.remove('active'));
    elemento.classList.add('active');
    
    // Guardar valor en el input oculto para enviarlo con el formulario
    document.getElementById('fecha-seleccionada').value = fecha;
    document.getElementById('hora-seleccionada').value = '';
    // Cargar las horas en el select
    cargarHoras(fecha); 
}

// Añade esta línea dentro de tu función seleccionarDia(elemento, fecha) existente,
// justo debajo de document.getElementById('fecha-seleccionada').value = fecha;
document.getElementById('hora-seleccionada').value = ''; 


// Sustituye tu función cargarHoras(fecha) por esta:
function cargarHoras(fecha) {
    const grupoHoras = document.getElementById('grupo-horas');
    const contenedorHoras = document.getElementById('contenedor-horas');

    // Mostramos la sección de horas y ponemos un mensaje de carga
    grupoHoras.style.display = 'block';
    contenedorHoras.innerHTML = '<p style="color: #aaa; grid-column: 1 / -1;">Buscando huecos...</p>';

    fetch(`/api/disponibilidad?fecha=${fecha}`)
        .then(response => response.json())
        .then(horas => {
            contenedorHoras.innerHTML = ''; // Limpiamos el mensaje
            
            if (horas.length === 0) {
                contenedorHoras.innerHTML = '<p style="color: #dc3545; grid-column: 1 / -1;">❌ No quedan huecos para este día.</p>';
            } else {
                // Creamos un botón div por cada hora disponible
                horas.forEach(h => {
                    const btn = document.createElement('div');
                    btn.className = 'hora-btn';
                    btn.textContent = h;
                    
                    // Al hacer clic, ejecuta seleccionarHora
                    btn.onclick = function() { seleccionarHora(this, h); };
                    
                    contenedorHoras.appendChild(btn);
                });
            }
        })
        .catch(error => {
            console.error("Error al cargar horas:", error);
            contenedorHoras.innerHTML = '<p style="color: #dc3545; grid-column: 1 / -1;">Error de conexión.</p>';
        });
}

// Nueva función para manejar el clic en los botones de hora
window.seleccionarHora = function(elemento, hora) {
    // 1. Quitar la clase 'active' de todas las horas
    document.querySelectorAll('.hora-btn').forEach(btn => btn.classList.remove('active'));
    
    // 2. Ponérsela solo a la que hemos hecho clic
    elemento.classList.add('active');
    
    // 3. Guardar el valor en el input oculto para que el formulario lo envíe
    document.getElementById('hora-seleccionada').value = hora;
}