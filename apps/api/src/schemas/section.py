# apps/api/src/schemas/section.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from src.schemas.candidate import Candidate

class SectionState(BaseModel):
    candidates: List[Candidate] = Field(default_factory=list)
    selected_id: Optional[str] = None
    selected_text: Optional[str] = None

    corpus_hits: List[Any] = Field(default_factory=list)
    rag_status: str = "unknown"
    rag_message: Optional[str] = None
    rag_query: Optional[str] = None