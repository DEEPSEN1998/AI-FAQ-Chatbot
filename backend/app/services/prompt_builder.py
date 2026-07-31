from typing import Dict, List
from langchain_core.documents import Document


class PromptBuilder:
    """
    RAG Prompt Builder with Section Isolation and Source Citation directives.

    Follows SOLID principles:
    - Single Responsibility: Formats system rules, context provenance, history, and questions into structured prompts.
    """

    def __init__(self, system_role: str = "K8ight Web Services"):
        """
        Initialize PromptBuilder.

        Args:
            system_role (str): Domain role description.
        """
        self.system_role = system_role

    def build_prompt(
        self,
        history: List[Dict[str, str]],
        documents: List[Document],
        question: str,
    ) -> str:
        """
        Build formatted RAG prompt with clear section boundaries and source citations.

        Args:
            history (List[Dict[str, str]]): List of conversation messages containing 'role' and 'content'.
            documents (List[Document]): Context documents with metadata.
            question (str): Current user question.

        Returns:
            str: Prompt text.
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
                f"Page Number: {page_number}\n"
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
You are the official AI assistant for {self.system_role}.

Your primary responsibility is to answer questions about the company accurately using ONLY the provided COMPANY CONTEXT below.

==================================================
CRITICAL RULES & BOUNDARIES
==================================================
1. Base your answer STRICTLY on the provided COMPANY CONTEXT. Never invent or extrapolate facts.
2. SECTION & PERSON ISOLATION: Never mix facts, roles, or skills from different individuals or different document sections. If the query asks about a specific person or section, use ONLY information explicitly belonging to that person or section.
3. If the answer cannot be determined from the provided context, state politely: "I do not have access to that information in our company knowledge base."


==================================================
COMPANY CONTEXT
==================================================
{context_text}

==================================================
CONVERSATION HISTORY
==================================================
{conversation_text}

==================================================
CURRENT QUESTION
==================================================
{question}

==================================================
ANSWER (With Source Citation at the end):
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