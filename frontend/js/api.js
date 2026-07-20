// =====================================
// Backend Configuration
// =====================================

const API_BASE_URL = "http://127.0.0.1:8000";


// =====================================
// Create Session ID (only once)
// =====================================

let sessionId = sessionStorage.getItem("session_id");

if (!sessionId) {
    sessionId = crypto.randomUUID();
    sessionStorage.setItem("session_id", sessionId);
}


// =====================================
// Ask AI
// =====================================

async function askAI(message) {

    try {

        const response = await fetch(`${API_BASE_URL}/chat`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                session_id: sessionId,
                message: message

            })

        });

        if (!response.ok) {
            throw new Error(`Server Error : ${response.status}`);
        }

        const data = await response.json();

        return data.response;

    }
    catch (error) {

        console.error(error);

        throw error;

    }

}