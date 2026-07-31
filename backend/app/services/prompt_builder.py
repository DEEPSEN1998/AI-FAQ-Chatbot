from typing import Dict, List
from langchain_core.documents import Document


class PromptBuilder:
    """
    RAG Prompt Builder for K8ight Web Services AI Assistant.

    Follows SOLID principles:
    - Single Responsibility: Formats system rules, context provenance, history, and questions into structured prompts.
    """

    def __init__(self, system_role: str = "K8ight Web Services"):
        self.system_role = system_role

    def build_prompt(
        self,
        history: List[Dict[str, str]],
        documents: List[Document],
        question: str,
    ) -> str:
        """
        Build clean RAG prompt grounding answer in retrieved company context without exposing internal metadata or raw citations to the end user.
        """
        formatted_context_blocks = []
        for idx, doc in enumerate(documents, start=1):
            meta = doc.metadata or {}
            source_file = meta.get("source_file", meta.get("source", "Unknown Document"))
            page_number = meta.get("page_number", meta.get("page", 1))
            section_name = meta.get("section_name", "General Context")
            chunk_id = meta.get("chunk_id", f"chunk_{idx}")

            block = (
                f"--- [CONTEXT CHUNK {idx}] ---\n"
                f"Source File: {source_file}\n"
                f"Page: {page_number}\n"
                f"Section: {section_name}\n"
                f"Chunk ID: {chunk_id}\n\n"
                f"{doc.page_content.strip()}"
            )
            formatted_context_blocks.append(block)

        context_text = (
            "\n\n".join(formatted_context_blocks)
            if formatted_context_blocks
            else "No specific context available."
        )

        conversation_lines = []
        for message in history:
            role = message.get("role", "user").capitalize()
            content = message.get("content", "")
            conversation_lines.append(f"{role}: {content}")
        conversation_text = (
            "\n".join(conversation_lines)
            if conversation_lines
            else "No previous conversation."
        )

        prompt = f"""
You are the official AI Assistant of {self.system_role}.

Your goal is to answer user inquiries clearly, accurately, and professionally based STRICTLY on the provided COMPANY CONTEXT below.

==================================================
CRITICAL SYSTEM INSTRUCTIONS
==================================================
1. IDENTITY: You are the AI Assistant of {self.system_role}. Never state or imply that you are Qwen, Llama, ChatGPT, OpenAI, or any underlying model architecture.
2. GROUNDING & ACCURACY: Base your response ONLY on the provided COMPANY CONTEXT. Never invent, speculate, or use external knowledge.
3. NO RAW CITATIONS IN TEXT: Do not print raw document names, page numbers, or "Source:" metadata blocks in your final text. Keep answers natural, polite, and conversational.
4. SECTION & PERSON ISOLATION: Do not mix skills, projects, or background between different individuals or separate sections.
5. FALLBACK RESPONSE: If the answer cannot be found in the provided context, answer politely:
   "I couldn't find that information in our company documents."

==================================================
COMPANY CONTEXT
==================================================
{context_text}

==================================================
CONVERSATION HISTORY
==================================================
{conversation_text}

==================================================
USER QUESTION
==================================================
{question}

==================================================
CONVERSATIONAL ANSWER:
==================================================
"""
        return prompt.strip()


def build_prompt(
    history: List[Dict[str, str]],
    documents: List[Document],
    question: str,
) -> str:
    """
    Backward-compatible functional interface for prompt building.
    """
    builder = PromptBuilder()
    return builder.build_prompt(history=history, documents=documents, question=question)