// =====================================
// UI Elements
// =====================================

const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");


// =====================================
// Auto Resize Textarea
// =====================================

messageInput.addEventListener("input", () => {

    messageInput.style.height = "auto";
    messageInput.style.height = messageInput.scrollHeight + "px";

});


// =====================================
// Scroll Chat to Bottom
// =====================================

function scrollToBottom() {

    chatBox.scrollTop = chatBox.scrollHeight;

}


// =====================================
// Clear Input
// =====================================

function clearInput() {

    messageInput.value = "";

    messageInput.style.height = "auto";

}


// =====================================
// Add User Message
// =====================================

function addUserMessage(message) {

    const html = `

        <div class="message user">

            <div class="bubble">

                ${message}

            </div>

            <div class="avatar">

                👤

            </div>

        </div>

    `;

    chatBox.insertAdjacentHTML("beforeend", html);

    scrollToBottom();

}


// =====================================
// Add Bot Message
// =====================================

function addBotMessage(message) {

    const html = `

        <div class="message bot">

            <div class="avatar">

                🤖

            </div>

            <div class="bubble">

                ${message}

            </div>

        </div>

    `;

    chatBox.insertAdjacentHTML("beforeend", html);

    scrollToBottom();

}


// =====================================
// Typing Indicator
// =====================================

function showTypingIndicator() {

    const html = `

        <div class="message bot" id="typingIndicator">

            <div class="avatar">

                🤖

            </div>

            <div class="bubble">

                <div class="typing">

                    <span></span>
                    <span></span>
                    <span></span>

                </div>

            </div>

        </div>

    `;

    chatBox.insertAdjacentHTML("beforeend", html);

    scrollToBottom();

}


// =====================================
// Remove Typing Indicator
// =====================================

function hideTypingIndicator() {

    const typing = document.getElementById("typingIndicator");

    if (typing) {

        typing.remove();

    }

}


// =====================================
// Enter to Send
// Shift + Enter = New Line
// =====================================

messageInput.addEventListener("keydown", (event) => {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendBtn.click();

    }

});