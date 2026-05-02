document.addEventListener('DOMContentLoaded', actualizarCalendario);

// static/js/reservas.js

async function actualizarCalendario() {
    try {
        // 1. Hacemos UNA ÚNICA petición al nuevo endpoint para obtener el resumen mensual
        const responseResumen = await fetch('/api/disponibilidad-mensual');
        const resumen = await responseResumen.json();
        
        // Asumimos que la API devuelve un array de fechas ocupadas
        const diasOcupadosCompletamente = resumen.dias_ocupados || []; 
        
        // 2. Además, podemos pedir los cierres totales si los mantienes en otra API
        const responseBloqueados = await fetch('/api/dias-ocupados');
        const diasBloqueados = await responseBloqueados.json();

        // Unimos ambos arrays para tener la lista completa de días sin citas
        const todosLosDiasInactivos = [...new Set([...diasBloqueados, ...diasOcupadosCompletamente])];

        const diasElements = document.querySelectorAll('.dia-itv');
        
        // 3. Iteramos por el DOM, ¡pero SIN hacer peticiones fetch aquí!
        for (let el of diasElements) {
            const fecha = el.getAttribute('data-fecha');
            
            if (todosLosDiasInactivos.includes(fecha)) {
                marcarOcupado(el); //[cite: 1]
            } else {
                marcarDisponible(el); //[cite: 1]
            }
        }
    } catch (error) {
        console.error("Error consultando disponibilidad:", error); //[cite: 1]
        // Si falla, es mejor marcar todo como ocupado o mostrar un mensaje de error global
        document.querySelectorAll('.dia-itv').forEach(marcarOcupado); 
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