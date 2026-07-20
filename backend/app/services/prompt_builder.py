def build_prompt(history):

    prompt = (
        "You are a helpful AI assistant for a company website.\n\n"
        "Conversation History:\n\n"
    )

    for message in history:

        role = message["role"].capitalize()
        content = message["content"]

        prompt += f"{role}: {content}\n"

    prompt += "\nAssistant:"

    return prompt