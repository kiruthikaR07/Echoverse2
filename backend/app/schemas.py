from typing import List, Dict, Any, Optional

try:
    from pydantic import BaseModel, Field

    class Message(BaseModel):
        role: str = Field(..., description="'user' or 'assistant'")
        content: str = Field(..., description="The content of the message")

    class Feedback(BaseModel):
        summary: str
        strengths: List[str]
        gaps: List[str]
        next: List[str]

    class InterviewRequest(BaseModel):
        sessionId: str
        candidate: Dict[str, Any]
        messages: Optional[List[Message]] = []

    class InterviewResponse(BaseModel):
        sessionId: str
        message: str
        done: bool
        feedback: Optional[Feedback] = None

except ImportError:
    from dataclasses import dataclass, field

    @dataclass
    class Message:
        role: str
        content: str

        def model_dump(self):
            return {"role": self.role, "content": self.content}

    @dataclass
    class Feedback:
        summary: str
        strengths: List[str] = field(default_factory=list)
        gaps: List[str] = field(default_factory=list)
        next: List[str] = field(default_factory=list)

    @dataclass
    class InterviewRequest:
        sessionId: str
        candidate: Dict[str, Any]
        messages: List[Message] = field(default_factory=list)

    @dataclass
    class InterviewResponse:
        sessionId: str
        message: str
        done: bool
        feedback: Optional[Feedback] = None
