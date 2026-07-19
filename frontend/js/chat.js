// =====================================
// Send Button
// =====================================

sendBtn.addEventListener("click", sendMessage);


// =====================================
// Main Chat Function
// =====================================

async function sendMessage() {

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    // Show User Message
    addUserMessage(message);

    // Clear Input
    clearInput();

    // Show Typing Animation
    showTypingIndicator();

    try {

        // Send message to API
        const response = await askAI(message);

        // Remove Typing
        hideTypingIndicator();

        // Show AI Response
        addBotMessage(response);

    }
    catch (error) {

        hideTypingIndicator();

        addBotMessage("❌ Something went wrong.");

        console.error(error);

    }

}