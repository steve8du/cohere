from typing import List
from pydantic import BaseModel

# Request/Response Models
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str
    used_wikipedia: bool = False

# History Models
class ChatHistoryEntry(BaseModel):
    conversation_id: str
    user_query: str
    response: str
    timestamp: str
    used_wikipedia: bool

class ChatHistoryResponse(BaseModel):
    history: List[ChatHistoryEntry]
    total_conversations: int