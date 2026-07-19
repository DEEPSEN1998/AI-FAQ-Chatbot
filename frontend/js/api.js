// =====================================
// Backend Configuration
// =====================================

const API_BASE_URL = "http://127.0.0.1:8000";


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