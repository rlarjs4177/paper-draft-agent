# apps/api/src/schemas/candidate.py
from pydantic import BaseModel

class Candidate(BaseModel):
    id: str
    text: str