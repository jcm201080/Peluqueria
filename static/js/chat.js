document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chatbot-toggle-btn");
    const closeBtn = document.getElementById("close-chat-btn");
    const chatWindow = document.getElementById("chatbot-window");
    const sendBtn = document.getElementById("send-chat-btn");
    const inputField = document.getElementById("chat-input-field");
    const messagesContainer = document.getElementById("chatbot-messages");

    // Abrir/Cerrar chat
    toggleBtn.addEventListener("click", () => chatWindow.classList.toggle("oculto"));
    closeBtn.addEventListener("click", () => chatWindow.classList.add("oculto"));

    // Función principal para enviar el mensaje
    const enviarMensaje = async () => {
        const texto = inputField.value.trim();
        if (texto === "") return;

        // 1. Mostramos el mensaje del usuario y limpiamos la caja
        agregarMensaje("usuario", texto);
        inputField.value = "";

        // 2. PROTECCIÓN: Bloqueamos el input y botón para que no envíen varios a la vez
        inputField.disabled = true;
        sendBtn.disabled = true;

        // 3. Creamos el mensaje temporal y guardamos su ID
        const loadingId = agregarMensaje("bot", "Escribiendo <span class='puntos-animados'>...</span>");

        try {
            const response = await fetch("/api/ia/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensaje: texto })
            });

            if (!response.ok) {
                const textError = await response.text();
                throw new Error(`Error del servidor (${response.status}): ${textError}`);
            }

            const data = await response.json();

            // 4. ÉXITO: Eliminamos el "Escribiendo..." del DOM
            const mensajeCarga = document.getElementById(loadingId);
            if (mensajeCarga) mensajeCarga.remove();

            // 5. Añadimos el mensaje final usando innerHTML para que los enlaces funcionen
            agregarMensaje("bot", data.respuesta);

        } catch (error) {
            console.error("Fallo exacto en el chat:", error);
            
            // 4B. ERROR: Eliminamos también el "Escribiendo..." si la conexión falla
            const mensajeCarga = document.getElementById(loadingId);
            if (mensajeCarga) mensajeCarga.remove();

            // 5B. Mostramos un mensaje visual de error
            agregarMensaje("bot", "⚠️ Hubo un error de conexión con mi sistema. Por favor, inténtalo de nuevo.");
        } finally {
            // 6. PASE LO QUE PASE: Volvemos a activar el cajón de texto
            inputField.disabled = false;
            sendBtn.disabled = false;
            inputField.focus(); // Devolvemos el cursor al cajón automáticamente
        }
    };

    sendBtn.addEventListener("click", enviarMensaje);
    inputField.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !sendBtn.disabled) {
            e.preventDefault(); // Evitamos saltos de línea raros en algunos navegadores
            enviarMensaje();
        }
    });

    // Función auxiliar para añadir mensajes al DOM
    function agregarMensaje(remitente, texto) {
        const div = document.createElement("div");
        div.className = `mensaje ${remitente}`;
        div.innerHTML = texto; // Clave para que procese los enlaces <a> de la IA

        // ID único garantizado combinando la fecha y un número aleatorio
        const id = 'msg-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        div.id = id;

        messagesContainer.appendChild(div);
        
        // Animación fluida de scroll
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: "smooth"
        });
        
        return id;
    }
});