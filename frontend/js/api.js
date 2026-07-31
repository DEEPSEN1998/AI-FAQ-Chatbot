// =====================================
// Backend Configuration
// =====================================

const API_BASE_URL = "http://127.0.0.1:8000";

// =====================================
// Create Session ID
// =====================================

let sessionId = sessionStorage.getItem("session_id");

if (!sessionId) {
    sessionId = crypto.randomUUID();
    sessionStorage.setItem("session_id", sessionId);
}

// =====================================
// Fetch Flat Models Array (GET /models)
// =====================================

async function fetchModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/models`);
        if (!response.ok) {
            throw new Error(`Failed to fetch models: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching models:", error);
        return [];
    }
}

// =====================================
// Token Streaming AI Request (SSE)
// =====================================

async function askAIStream(message, model, onToken, onError, onComplete) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
                model: model,
                stream: true,
            }),
        });

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            if (chunk) {
                onToken(chunk);
            }
        }

        if (onComplete) onComplete();

    } catch (error) {
        console.error("Stream Error:", error);
        if (onError) onError(error);
    }
}

// =====================================
// Synchronous Ask AI Request
// =====================================

async function askAI(message, model) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
                model: model,
            }),
        });

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error("Chat Error:", error);
        throw error;
    }
}