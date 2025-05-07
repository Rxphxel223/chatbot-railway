let generalMessages = [];

function sendGeneralMessage() {
    const input = document.getElementById("general-user-input");
    const chatBox = document.getElementById("general-chat-box");
    const userText = input.value.trim();
    if (!userText) return;


    chatBox.innerHTML += `<div class="user-message">${userText}</div>`;
    input.value = "";


    const typing = document.createElement("div");
    typing.className = "bot-message";
    typing.innerText = "RaphaelGPT tippt...";
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;

    
    generalMessages.push({ role: "user", content: userText });

    fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer DEIN_API_KEY_HIER"
        },
        body: JSON.stringify({
            model: "gpt-3.5-turbo",
            messages: generalMessages
        })
    })
    .then(res => res.json())
    .then(data => {
        typing.remove();
        const reply = data.choices[0].message.content;
        generalMessages.push({ role: "assistant", content: reply });

        chatBox.innerHTML += `<div class="bot-message">${reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(err => {
        typing.remove();
        chatBox.innerHTML += `<div class="bot-message">⚠️ Fehler beim Laden: ${err.message}</div>`;
    });
}

function handleGeneralKeyPress(event) {
    if (event.key === "Enter") {
        sendGeneralMessage();
    }
}
