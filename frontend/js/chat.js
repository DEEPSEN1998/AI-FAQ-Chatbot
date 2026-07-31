// ================================
// Model Registry State Management
// ================================

let availableModels = [];

async function initModelSelector() {
    availableModels = await fetchModels();
    if (!availableModels || availableModels.length === 0) return;

    modelSelect.innerHTML = "";

    const localGroup = document.createElement("optgroup");
    localGroup.label = "🟢 Local Models";

    const cloudGroup = document.createElement("optgroup");
    cloudGroup.label = "☁️ Cloud Models";

    availableModels.forEach((m) => {
        const option = document.createElement("option");
        option.value = m.id;
        option.textContent = m.display_name + (m.online ? "" : " (Offline)");

        if (m.category === "Cloud") {
            cloudGroup.appendChild(option);
        } else {
            localGroup.appendChild(option);
        }
    });

    if (localGroup.children.length > 0) {
        modelSelect.appendChild(localGroup);
    }
    if (cloudGroup.children.length > 0) {
        modelSelect.appendChild(cloudGroup);
    }

    // Restore saved model selection from localStorage
    const savedModel = localStorage.getItem("selected_model");
    if (savedModel && availableModels.some((m) => m.id === savedModel)) {
        modelSelect.value = savedModel;
    } else if (modelSelect.options.length > 0) {
        localStorage.setItem("selected_model", modelSelect.value);
    }

    // Save selection on change
    modelSelect.addEventListener("change", () => {
        localStorage.setItem("selected_model", modelSelect.value);
    });
}

document.addEventListener("DOMContentLoaded", initModelSelector);


// ================================
// Main Chat Function (Streaming)
// ================================

sendBtn.addEventListener("click", sendMessage);

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    const selectedModelId = modelSelect.value;
    const modelObj = availableModels.find((m) => m.id === selectedModelId);
    const modelDisplayName = modelObj ? modelObj.display_name : selectedModelId;
    const modelCategory = modelObj ? modelObj.category : "Local";

    // 1. Render User Message & Clear Input
    addUserMessage(message);
    clearInput();

    // 2. Show Typing Indicator
    showTyping();

    let bubbleElement = null;

    // 3. Trigger Token Streaming API sending ONLY model ID
    askAIStream(
        message,
        selectedModelId,
        // On Token Received
        (token) => {
            hideTyping();
            if (!bubbleElement) {
                bubbleElement = addBotStreamBubble(modelDisplayName, modelCategory);
            }
            appendStreamToken(bubbleElement, token);
        },
        // On Error
        (error) => {
            hideTyping();
            if (!bubbleElement) {
                addBotMessage(
                    "❌ Request failed. Please verify local model status or API key settings.",
                    modelDisplayName,
                    modelCategory
                );
            } else {
                appendStreamToken(bubbleElement, "\n\n❌ Connection error.");
            }
        },
        // On Streaming Complete
        () => {
            hideTyping();
        }
    );
}