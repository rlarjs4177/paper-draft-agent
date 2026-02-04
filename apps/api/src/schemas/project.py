# apps/api/src/schemas/project.py
from pydantic import BaseModel
from typing import Dict, Literal
from src.schemas.section import SectionState

SectionName = Literal["introduction", "dataset", "method", "conclusion"]
SECTIONS = ["introduction", "dataset", "method", "conclusion"]

class ProjectState(BaseModel):
    project_id: str
    user_input: str
    stage: SectionName
    sections: Dict[SectionName, SectionState]
