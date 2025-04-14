let questionCount = 0;
const maxQuestions = 10;
let token = localStorage.getItem("accessToken");

document.addEventListener("DOMContentLoaded", () => {
    checkLogin();

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `
        <div class="bot-message">
            👋 Willkommen! Ich bin hier, damit du Raphael besser kennenlernen kannst. 
            Ich beantworte deine Fragen über Raphael aus der Sicht seines besten Freundes. 
            Für die besten Ergebnisse formuliere deine Fragen bitte so, dass der Name „Raphael“ darin vorkommt. 
            Du kannst mir bis zu ${maxQuestions} Fragen stellen – leg gerne los!
        </div>
    `;

    document.getElementById("password").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            checkPassword();
        }
    });
});

function checkLogin() {
    if (token) {
        document.getElementById("login-screen").style.display = "none";
        document.getElementById("main-content").style.display = "block";
    }
}

function checkPassword() {
    const password = document.getElementById("password").value;
    const rememberMe = document.getElementById("remember-me").checked;

    fetch("https://chatbot-api-xw3r.onrender.com/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.token) {
            token = data.token;
            if (rememberMe) {
                localStorage.setItem("accessToken", token);
            }
            document.getElementById("login-screen").style.display = "none";
            document.getElementById("main-content").style.display = "block";
        } else {
            alert("Falsches Passwort!");
        }
    })
    .catch(err => {
        console.error("Login-Fehler:", err);
    });
}

function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (!userInput.trim()) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div class="user-message">${userInput}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    // Typing Indicator anzeigen
    const typingIndicator = document.createElement("div");
    typingIndicator.className = "bot-message typing-indicator";
    typingIndicator.innerHTML = `<span></span><span></span><span></span>`;
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("https://chatbot-api-xw3r.onrender.com/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ question: userInput })
    })
    .then(res => res.json())
    .then(data => {
        typingIndicator.remove();
        if (data.answer) {
            chatBox.innerHTML += `<div class="bot-message">${data.answer}</div>`;
        } else {
            chatBox.innerHTML += `<div class="bot-message">❌ Fehler: ${data.error}</div>`;
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(err => {
        typingIndicator.remove();
        chatBox.innerHTML += `<div class="bot-message">❌ Fehler: Anfrage fehlgeschlagen.</div>`;
        console.error("Fehler:", err);
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    document.getElementById("user-input").value = "";
}

function logout() {
    localStorage.removeItem("accessToken");
    token = null;
    document.getElementById("login-screen").style.display = "block";
    document.getElementById("main-content").style.display = "none";
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
