const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const modelSelect = document.getElementById("modelSelect");

// ----------------------------
// Escape HTML to prevent layout breaking / XSS
// ----------------------------
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

// ----------------------------
// Auto resize textarea
// ----------------------------
messageInput.addEventListener("input", () => {
    messageInput.style.height = "auto";
    messageInput.style.height = messageInput.scrollHeight + "px";
});

// ----------------------------
// Smooth scroll to bottom
// ----------------------------
function scrollToBottom() {
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
    });
}

// ----------------------------
// Remove welcome screen
// ----------------------------
function removeWelcome() {
    const welcome = document.querySelector(".welcome");
    if (welcome) {
        welcome.remove();
    }
}

// ----------------------------
// User Message
// ----------------------------
function addUserMessage(text) {
    removeWelcome();

    const message = document.createElement("div");
    message.className = "message user";
    message.innerHTML = `<div class="bubble">${escapeHTML(text)}</div>`;

    chatBox.appendChild(message);
    scrollToBottom();
}

// ----------------------------
// Streaming AI Message with Model Badge
// ----------------------------
function addBotStreamBubble(modelDisplayName, category = "Local") {
    removeWelcome();

    const icon = category === "Cloud" ? "☁️" : "🟢";
    const badgeText = `${icon} ${modelDisplayName}`;

    const message = document.createElement("div");
    message.className = "message ai";

    message.innerHTML = `
        <div class="model-badge">${escapeHTML(badgeText)}</div>
        <div class="bubble stream-bubble"></div>
    `;

    chatBox.appendChild(message);
    scrollToBottom();

    return message.querySelector(".stream-bubble");
}

// ----------------------------
// Append Stream Token
// ----------------------------
function appendStreamToken(bubbleElement, token) {
    if (!bubbleElement) return;
    bubbleElement.textContent += token;
    scrollToBottom();
}

// ----------------------------
// Static AI Message
// ----------------------------
function addBotMessage(text, modelDisplayName = "", category = "Local") {
    removeWelcome();

    const icon = category === "Cloud" ? "☁️" : "🟢";
    const badgeHtml = modelDisplayName ? `<div class="model-badge">${icon} ${escapeHTML(modelDisplayName)}</div>` : "";

    const message = document.createElement("div");
    message.className = "message ai";
    message.innerHTML = `
        ${badgeHtml}
        <div class="bubble">${text}</div>
    `;

    chatBox.appendChild(message);
    scrollToBottom();
}

// ----------------------------
// Typing Indicator
// ----------------------------
function showTyping() {
    removeWelcome();
    if (document.getElementById("typing")) return;

    const typingElement = document.createElement("div");
    typingElement.className = "message ai";
    typingElement.id = "typing";
    typingElement.innerHTML = `
        <div class="bubble">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatBox.appendChild(typingElement);
    scrollToBottom();
}

function hideTyping() {
    const typing = document.getElementById("typing");
    if (typing) {
        typing.remove();
    }
}

// ----------------------------
// Clear Input
// ----------------------------
function clearInput() {
    messageInput.value = "";
    messageInput.style.height = "auto";
}

// ----------------------------
// Enter Key handling
// ----------------------------
messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});