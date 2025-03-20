let questionCount = 0;
const maxQuestions = 10;

// Prüft, ob der Nutzer eingeloggt ist (lokale Speicherung beachten)
function checkLogin() {
    let remembered = localStorage.getItem("rememberMe");
    if (remembered === "true") {
        document.getElementById("login-screen").style.display = "none";
        document.getElementById("main-content").style.display = "block";
    } else {
        fetch("https://chatbot-api-xw3r.onrender.com/login", {
            method: "POST",
            credentials: "include"
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById("login-screen").style.display = "none";
                document.getElementById("main-content").style.display = "block";
            }
        });
    }
}
function checkPassword() {
    let password = document.getElementById("password").value;
    let rememberMe = document.getElementById("remember-me").checked;

    fetch("https://chatbot-api-xw3r.onrender.com/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",  // 🛠 FIX: Sende Session-Cookies mit!
        body: JSON.stringify({ password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert("Login erfolgreich!");
            document.getElementById("login-screen").style.display = "none";
            document.getElementById("main-content").style.display = "block";

            if (rememberMe) {
                localStorage.setItem("rememberMe", "true");
            }
        } else {
            alert("Falsches Passwort!");
        }
    })
    .catch(error => {
        console.error("Login-Fehler:", error);
    });
}

function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (!userInput.trim()) return;

    let chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div><strong>Du:</strong> ${userInput}</div>`;

    fetch("https://chatbot-api-xw3r.onrender.com/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",  // 🛠 FIX: Sendet Session-Cookie mit!
        body: JSON.stringify({ question: userInput })
    })
    .then(response => response.json())
    .then(data => {
        if (data.answer) {
            chatBox.innerHTML += `<div><strong>Chatbot:</strong> ${data.answer}</div>`;
        } else {
            chatBox.innerHTML += `<div><strong>Fehler:</strong> ${data.error}</div>`;
        }
    })
    .catch(error => {
        chatBox.innerHTML += `<div><strong>Fehler:</strong> Anfrage fehlgeschlagen.</div>`;
        console.error("Fehler:", error);
    });

    document.getElementById("user-input").value = "";
}
// Meldet den Nutzer ab und löscht gespeicherte Daten
function logout() {
    fetch("https://chatbot-api-xw3r.onrender.com/logout", {
        method: "POST",
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        alert("Du bist jetzt ausgeloggt.");
        document.getElementById("login-screen").style.display = "block";
        document.getElementById("main-content").style.display = "none";
        localStorage.removeItem("rememberMe"); // Entfernt den gespeicherten Login-Status
    });
}

// Prüft, ob Enter gedrückt wurde und sendet die Nachricht
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
