from backend.app.llm.ollama_service import call_ollama
from backend.app.services.prompt_builder import build_prompt
from backend.app.services.memory_service import add_message, get_history
from backend.app.rag.retriever import retrieve_documents


def chat_with_ai(session_id: str, message: str):

    # Save user message
    add_message(session_id, "user", message)

    # Conversation history
    history = get_history(session_id)[-10:]

    # Determine retrieval size
    message_lower = message.lower()

    list_keywords = [
        "portfolio",
        "projects",
        "project",
        "all",
        "list",
        "show",
        "services",
        "technologies",
        "team",
        "developers",
        "employees"
    ]

    k = 10 if any(keyword in message_lower for keyword in list_keywords) else 4

    # Retrieve documents with similarity scores
    results = retrieve_documents(message, k=k)

    documents = []

    print("\n========== RETRIEVED DOCUMENTS ==========\n")

    for document, score in results:

        print(f"Score: {score:.4f}")
        print(document.page_content[:250])
        print("-" * 60)

        # Keep only the Document
        documents.append(document)

    # Build prompt
    prompt = build_prompt(
        history=history,
        documents=documents,
        question=message,
    )

    # Uncomment for debugging
    # print(prompt)

    # Generate response
    response = call_ollama(prompt)

    # Save assistant response
    add_message(session_id, "assistant", response)

    return response