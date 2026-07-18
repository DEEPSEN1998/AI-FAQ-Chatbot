import requests
from fastapi import HTTPException


def call_ollama(message: str):
    url = "http://localhost:11434/api/generate"

    data = {
        "model": "qwen2.5:3b",
        "prompt": message,
        "stream": False
    }

    try:
        response = requests.post(url, json=data)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Ollama returned an error."
            )

        result = response.json()
        return result["response"]

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to connect to Ollama: {str(e)}"
        )