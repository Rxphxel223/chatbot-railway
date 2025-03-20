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

// Überprüft das eingegebene Passwort und speichert Login-Status
function checkPassword() {
    let password = document.getElementById("password").value;
    let rememberMe = document.getElementById("remember-me").checked; // Prüft, ob Checkbox aktiviert ist

    fetch("https://chatbot-api-xw3r.onrender.com/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert("Login erfolgreich!");
            document.getElementById("login-screen").style.display = "none";
            document.getElementById("main-content").style.display = "block";

            if (rememberMe) {
                localStorage.setItem("rememberMe", "true"); // Speichert den Login-Status
            }
        } else {
            alert("Falsches Passwort!");
        }
    });
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

// Nachricht senden (per Button oder Enter)
function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (!userInput.trim()) return;  // Falls kein Text eingegeben wurde, nichts senden

    // Nutzer-Eingabe anzeigen
    let chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div><strong>Du:</strong> ${userInput}</div>`;

    // Anfrage an die API senden
    fetch("https://chatbot-api-xw3r.onrender.com/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",  // Wichtig: Sendet die Session-Cookies mit!
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

    // Eingabefeld leeren
    document.getElementById("user-input").value = "";
}

// Prüft, ob Enter gedrückt wurde und sendet die Nachricht
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
