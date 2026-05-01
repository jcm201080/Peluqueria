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

            const data = await response.json();

            // REPARACIÓN CLAVE: Usar innerHTML aquí también para que el enlace sea clicable
            const mensajeBotElement = document.getElementById(loadingId);
            mensajeBotElement.innerHTML = data.respuesta;

        } catch (error) {
            document.getElementById(loadingId).innerText = "Hubo un error de conexión.";
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