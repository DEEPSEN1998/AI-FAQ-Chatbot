const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");

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
// AI Message
// ----------------------------
function addBotMessage(text) {
    removeWelcome();

    const message = document.createElement("div");
    message.className = "message ai";
    
    // AI messages can contain HTML or markdown links, but we sanitize them minimally
    // or just let them render. Since they come from backend LLM, we use innerHTML 
    // but ensure standard formatting.
    message.innerHTML = `<div class="bubble">${text}</div>`;

    chatBox.appendChild(message);
    scrollToBottom();
}

// ----------------------------
// Typing Indicator
// ----------------------------
let typingElement = null;

function showTyping() {
    removeWelcome();

    // Prevent duplicate typing indicators
    if (document.getElementById("typing")) return;

    typingElement = document.createElement("div");
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
    typingElement = null;
}

// ----------------------------
// Clear Input
// ----------------------------
function clearInput() {
    messageInput.value = "";
    messageInput.style.height = "auto";
}

// ----------------------------
// Enter Key handling (Submit on enter, new line on shift+enter)
// ----------------------------
messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});