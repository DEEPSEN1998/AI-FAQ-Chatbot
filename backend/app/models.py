"""Request and response schemas shared by the API routes."""

from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class ChatRequest(BaseModel):
    """A single FAQ question. Conversation state is intentionally not persisted."""

    message: Annotated[str, Field(min_length=1, max_length=2_000)]


class ChatResponse(BaseModel):
    """Grounded answer with friendly source names for transparency."""

    answer: str
    sources: list[str]


class LeadCreate(BaseModel):
    """Fields collected by the website's lead-generation form."""

    name: Annotated[str, Field(min_length=2, max_length=120)]
    email: EmailStr
    company: str | None = Field(default=None, max_length=160)
    message: str | None = Field(default=None, max_length=2_000)


class LeadResponse(BaseModel):
    """Public confirmation returned after a lead has been safely stored."""

    id: int
    message: str
