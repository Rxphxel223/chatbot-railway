let questionCount = 0;
const maxQuestions = 10;


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


    chatBox.innerHTML += `
        <div class="user-message">${userInput}</div>
    `;


    chatBox.scrollTop = chatBox.scrollHeight;


    fetch("https://chatbot-api-xw3r.onrender.com/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", 
        body: JSON.stringify({ question: userInput })
    })
    .then(response => response.json())
    .then(data => {
        if (data.answer) {
            chatBox.innerHTML += `
                <div class="bot-message">${data.answer}</div>
            `;
        } else {
            chatBox.innerHTML += `
                <div class="bot-message">❌ Fehler: ${data.error}</div>
            `;
        }

        
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        chatBox.innerHTML += `
            <div class="bot-message">❌ Fehler: Anfrage fehlgeschlagen.</div>
        `;
        console.error("Fehler:", error);
    });

    document.getElementById("user-input").value = "";
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
        localStorage.removeItem("rememberMe"); // Entfernt den gespeicherten Login-Status
    });
}


function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
