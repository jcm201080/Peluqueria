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

    // Enviar mensaje
    // static/js/chat.js

    const enviarMensaje = async () => {
        const texto = inputField.value.trim();
        if (texto === "") return;

        agregarMensaje("usuario", texto);
        inputField.value = "";

        const loadingId = agregarMensaje("bot", "Escribiendo...");

        try {
            const response = await fetch("/api/ia/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensaje: texto })
            });

            // Si la respuesta no es 200 OK, lanzamos un error a propósito
            if (!response.ok) {
                const textError = await response.text(); // Leemos qué nos ha devuelto realmente el servidor
                throw new Error(`Error del servidor (${response.status}): ${textError}`);
            }

            const data = await response.json();

            // REPARACIÓN CLAVE: Usar innerHTML aquí también para que el enlace sea clicable
            const mensajeBotElement = document.getElementById(loadingId);
            mensajeBotElement.innerHTML = data.respuesta;

        } catch (error) {
            // Imprimimos el error REAL en la consola oculta para poder investigar
            console.error("Fallo exacto en el chat:", error);
            
            // Le mostramos un mensaje amigable al usuario
            document.getElementById(loadingId).innerText = "Hubo un error de conexión. Por favor, inténtalo de nuevo.";
        }
    };

    sendBtn.addEventListener("click", enviarMensaje);
    inputField.addEventListener("keypress", (e) => {
        if (e.key === "Enter") enviarMensaje();
    });

    // Función auxiliar para añadir mensajes al DOM
    // Localiza tu función de agregar mensajes en static/js/chat.js
    function agregarMensaje(remitente, texto) {
        const div = document.createElement("div");
        div.className = `mensaje ${remitente}`;

        // CAMBIO CLAVE: Usar innerHTML para que reconozca los enlaces <a>
        div.innerHTML = texto;

        const id = 'msg-' + Date.now();
        div.id = id;

        const messagesContainer = document.getElementById("chatbot-messages");
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return id;
    }
});