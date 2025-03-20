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

    fetch('https://mein-api.up.railway.app/ask', {  // ⚠ HIER deine Railway-URL einfügen
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
