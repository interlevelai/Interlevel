"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")


class UserResponse(BaseModel):
    user_id: str
    email: str
    token_balance: int
    created_at: datetime

    class Config:
        from_attributes = True


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class AgentResponse(BaseModel):
    agent_id: str
    user_id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    execution_id: str
    agent_id: str
    status: str
    tokens_used: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    output: Optional[str]

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class Message(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ConversationState(BaseModel):
    messages: List[Message]
    metadata: Optional[Dict[str, Any]] = {}
