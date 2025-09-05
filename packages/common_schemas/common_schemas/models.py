from pydantic import BaseModel, Field
from typing import List, Optional

class Question(BaseModel):
    id: str
    text: str
    options: List[str]
    correct: List[int] = Field(default_factory=list)
    time_limit_s: int = 20
    media: Optional[str] = None

class Quiz(BaseModel):
    id: Optional[str] = None
    org_id: Optional[str] = None
    owner_id: Optional[str] = None
    title: str
    locale: str = "pt-BR"
    questions: List[Question]

class SessionCreate(BaseModel):
    quiz_id: str

class SessionState(BaseModel):
    session_id: str
    state: str  # lobby|question|results|ended
    current_q_idx: int = 0

class JoinRequest(BaseModel):
    pin: str
    nickname: str

class AnswerRequest(BaseModel):
    question_id: str
    selected: List[int]
