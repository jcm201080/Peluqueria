document.addEventListener('DOMContentLoaded', actualizarCalendario);

async function actualizarCalendario() {
    try {
        const responseResumen = await fetch('/api/disponibilidad-mensual');
        const resumen = await responseResumen.json();
        
        const diasOcupadosCompletamente = resumen.dias_ocupados || []; 
        
        const responseBloqueados = await fetch('/api/dias-ocupados');
        const diasBloqueados = await responseBloqueados.json();

        const todosLosDiasInactivos = [...new Set([...diasBloqueados, ...diasOcupadosCompletamente])];

        const diasElements = document.querySelectorAll('.dia-itv');
        
        for (let el of diasElements) {
            const fecha = el.getAttribute('data-fecha');
            
            if (todosLosDiasInactivos.includes(fecha)) {
                marcarOcupado(el); 
            } else {
                marcarDisponible(el); 
            }
        }
    } catch (error) {
        console.error("Error consultando disponibilidad:", error); 
        document.querySelectorAll('.dia-itv').forEach(marcarOcupado); 
    }
}

function marcarOcupado(elemento) {
    elemento.classList.add('ocupado');
    elemento.classList.remove('disponible');
    elemento.onclick = null;
}

function marcarDisponible(elemento) {
    elemento.classList.add('disponible');
    elemento.classList.remove('ocupado');
}

window.seleccionarDia = function(elemento, fecha) {
    if (elemento.classList.contains('ocupado')) return;
    
    document.querySelectorAll('.dia-itv').forEach(d => d.classList.remove('active'));
    elemento.classList.add('active');
    
    document.getElementById('fecha-seleccionada').value = fecha;
    document.getElementById('hora-seleccionada').value = '';
    
    cargarHoras(fecha); 
}

function cargarHoras(fecha) {
    const grupoHoras = document.getElementById('grupo-horas');
    const contenedorHoras = document.getElementById('contenedor-horas');

    grupoHoras.style.display = 'block';
    contenedorHoras.innerHTML = '<p style="color: #aaa; grid-column: 1 / -1;">Buscando huecos...</p>';

    fetch(`/api/disponibilidad?fecha=${fecha}`)
        .then(response => response.json())
        .then(datos => {
            contenedorHoras.innerHTML = ''; 
            
            if (!datos || datos.length === 0) {
                contenedorHoras.innerHTML = '<p style="color: #dc3545; grid-column: 1 / -1;">❌ No quedan huecos para este día.</p>';
                return;
            }

            // LEEMOS LA CONFIGURACIÓN DEL HTML
            const mostrarPeluquero = contenedorHoras.getAttribute('data-mostrar-peluquero') === 'true';
            
            let huecosProcesados = [];

            if (mostrarPeluquero) {
                // Si mostramos peluqueros, volcamos todas las combinaciones (Ej: 10:00 - Jose, 10:00 - Antonio)
                huecosProcesados = datos;
            } else {
                // Si NO mostramos peluqueros, agrupamos por hora para que no salgan botones duplicados
                const horasVistas = new Set();
                huecosProcesados = datos.filter(h => {
                    const horaTexto = typeof h === 'string' ? h : h.hora;
                    if (horasVistas.has(horaTexto)) return false;
                    horasVistas.add(horaTexto);
                    return true;
                });
            }

            // PINTAMOS LOS BOTONES
            huecosProcesados.forEach(hueco => {
                const horaTexto = typeof hueco === 'string' ? hueco : hueco.hora;
                const peluqueroId = typeof hueco === 'object' ? hueco.peluquero_id : '';
                const peluqueroNombre = typeof hueco === 'object' ? hueco.peluquero_nombre : '';

                const btn = document.createElement('div');
                btn.className = 'hora-btn btn-hora'; 
                
                let htmlContenido = `<span>${horaTexto}</span>`;
                
                if (mostrarPeluquero && peluqueroNombre) {
                    htmlContenido += `<span class="tag-peluquero">${peluqueroNombre}</span>`;
                }
                
                btn.innerHTML = htmlContenido;
                
                // Al hacer click, enviamos tanto la hora como el ID del profesional
                btn.onclick = function() { seleccionarHora(this, horaTexto, peluqueroId); };
                
                contenedorHoras.appendChild(btn);
            });
        })
        .catch(error => {
            console.error("Error al cargar horas:", error);
            contenedorHoras.innerHTML = '<p style="color: #dc3545; grid-column: 1 / -1;">Error de conexión.</p>';
        });
}

window.seleccionarHora = function(elemento, hora, peluquero_id) {
    document.querySelectorAll('.hora-btn').forEach(btn => btn.classList.remove('active', 'seleccionado'));
    elemento.classList.add('active', 'seleccionado');
    
    // Guardamos la hora
    document.getElementById('hora-seleccionada').value = hora;

    // MAGIA: Creamos un input oculto al vuelo para enviar el ID del peluquero al backend si existe
    let inputPeluquero = document.getElementById('input-peluquero-dinamico');
    if (!inputPeluquero) {
        inputPeluquero = document.createElement('input');
        inputPeluquero.type = 'hidden';
        inputPeluquero.name = 'peluquero_id'; // Coincide con tu request.form.get('peluquero_id') en backend
        inputPeluquero.id = 'input-peluquero-dinamico';
        document.querySelector('form').appendChild(inputPeluquero);
    }
    
    // Si la opción de elegir peluquero está oculta o no aplica, se manda vacío y el backend autoasigna.
    inputPeluquero.value = peluquero_id || '';
}