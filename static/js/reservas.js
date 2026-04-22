document.getElementById('fecha-reserva').addEventListener('change', function() {
    const fecha = this.value;
    const horaSelect = document.getElementById('hora-reserva');

    // Desactivar y limpiar mientras carga
    horaSelect.disabled = true;
    horaSelect.innerHTML = '<option>Buscando huecos...</option>';

    fetch(`/api/disponibilidad?fecha=${fecha}`)
        .then(response => response.json())
        .then(horas => {
            horaSelect.innerHTML = ''; // Limpiar
            
            if (horas.length === 0) {
                const opt = document.createElement('option');
                opt.textContent = "No hay citas disponibles";
                horaSelect.appendChild(opt);
            } else {
                // Añadimos una opción vacía inicial
                horaSelect.innerHTML = '<option value="" disabled selected>Selecciona hora (Verde = Disponible)</option>';
                
                horas.forEach(h => {
                    const opt = document.createElement('option');
                    opt.value = h;
                    opt.textContent = h + " - Disponible";
                    opt.style.color = "green"; // Visualmente verde
                    horaSelect.appendChild(opt);
                });
                horaSelect.disabled = false;
            }
        });
});