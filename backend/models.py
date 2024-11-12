from pydantic import BaseModel
from typing import Dict

class LLMResponse(BaseModel):
    explanation: str
    files: Dict[str, str]