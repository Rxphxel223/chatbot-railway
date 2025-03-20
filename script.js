let questionCount = 0;
const maxQuestions = 10;

function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (!userInput.trim()) return;

    if (questionCount >= maxQuestions) {
        alert("Du hast das Frage-Limit von 10 erreicht.");
        return;
    }

    questionCount++;

    let chatBox = document.getElementById("chat-box");
    let userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    fetch('https://chatbot-api-xw3r.onrender.com/ask', {  // ⚠ HIER deine Railway-URL einfügen
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userInput })
    })
    .then(response => response.json())
    .then(data => {
        let botMessage = document.createElement("div");
        botMessage.className = "bot-message";
        botMessage.textContent = data.answer;
        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    });

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
