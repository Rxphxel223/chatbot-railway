let questionCount = 0;
const maxQuestions = 10;

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

function checkLogin() {
    fetch("https://chatbot-api-xw3r.onrender.com/login", {
        method: "POST",
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // Falls bereits eingeloggt, Chat anzeigen
            document.getElementById("login-screen").style.display = "none";
            document.getElementById("main-content").style.display = "block";
        }
    });
}

function checkPassword() {
    let password = document.getElementById("password").value;

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
        } else {
            alert("Falsches Passwort!");
        }
    });
}

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
    });
}
