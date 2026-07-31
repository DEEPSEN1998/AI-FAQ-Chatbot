import re
from enum import Enum
from typing import Dict, Optional, Tuple


class QueryCategory(str, Enum):
    """Enumeration of supported query categories for intent routing."""

    GREETING = "greeting"
    FAREWELL = "farewell"
    THANKS = "thanks"
    SMALL_TALK = "small_talk"
    COMPANY_QUESTION = "company_question"


class QueryRouter:
    """
    Intelligent Query Router service that classifies user incoming messages
    and determines whether they require RAG/LLM invocation or can be answered immediately.

    Follows SOLID principles:
    - Single Responsibility: Only responsible for intent classification and immediate response lookup.
    - Open/Closed: Easily extendable with custom rules/responses without mutating existing logic.
    """

    def __init__(self, predefined_responses: Optional[Dict[QueryCategory, str]] = None):
        # Default predefined responses for non-company questions
        self.predefined_responses: Dict[QueryCategory, str] = predefined_responses or {
            QueryCategory.GREETING: (
                "Hello! Welcome to K8ight Web Services. How can I help you today?"
            ),
            QueryCategory.FAREWELL: (
                "Goodbye! Have a great day and feel free to reach out anytime."
            ),
            QueryCategory.THANKS: (
                "You're welcome! Let me know if you need help with anything else."
            ),
            QueryCategory.SMALL_TALK: (
                "I am the official AI assistant for K8ight Web Services. "
                "I can help answer questions regarding our services, portfolio, technologies, and team!"
            ),
        }

        # Regex pattern mapping for pattern matching
        self._patterns = [
            (
                QueryCategory.GREETING,
                re.compile(
                    r"^(hi+|hello+|hey+|good\s*(morning|afternoon|evening|day)|greetings)(\s+.*)?$",
                    re.IGNORECASE,
                ),
            ),
            (
                QueryCategory.FAREWELL,
                re.compile(
                    r"^(bye+|goodbye+|see\s*you|take\s*care|cya)(\s+.*)?$",
                    re.IGNORECASE,
                ),
            ),
            (
                QueryCategory.THANKS,
                re.compile(
                    r"^(thanks+|thank\s*you|thx|much\s*appreciated)(\s+.*)?$",
                    re.IGNORECASE,
                ),
            ),
            (
                QueryCategory.SMALL_TALK,
                re.compile(
                    r"^(who\s*are\s*you|what\s*can\s*you\s*do|how\s*are\s*you|what\s*is\s*your\s*name|are\s*you\s*a\s*bot)(\s+.*)?$",
                    re.IGNORECASE,
                ),
            ),
        ]

    def classify_and_route(self, query: str) -> Tuple[QueryCategory, Optional[str]]:
        """
        Classifies a user query into a QueryCategory and returns an immediate response if applicable.

        Args:
            query (str): Cleaned raw string input from user.

        Returns:
            Tuple[QueryCategory, Optional[str]]: A tuple containing the category and optional predefined response string.
            If category is COMPANY_QUESTION, response will be None.
        """
        clean_query = query.strip()
        if not clean_query:
            return QueryCategory.GREETING, self.predefined_responses[QueryCategory.GREETING]

        # Evaluate pattern matching rules
        for category, pattern in self._patterns:
            if pattern.match(clean_query):
                return category, self.predefined_responses.get(category)

        # Default fallback to RAG pipeline for company queries
        return QueryCategory.COMPANY_QUESTION, None
