// ================================
// Send Button
// ================================

sendBtn.addEventListener("click", sendMessage);


// ================================
// Main Chat Function
// ================================

async function sendMessage() {

    const message = messageInput.value.trim();

    if (!message) return;

    // Show User Message
    addUserMessage(message);

    // Clear Input
    clearInput();

    // Show Typing
    showTyping();

    try {

        const response = await askAI(message);

        hideTyping();

        addBotMessage(response);

    }
    catch (error) {

        hideTyping();

        addBotMessage("❌ Something went wrong.");

        console.error(error);

    }

}