from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str
    provider: Optional[str] = None
    model: Optional[str] = None
    stream: Optional[bool] = False