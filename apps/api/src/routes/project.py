# apps/api/src/routes/project.py
from fastapi import APIRouter
from pydantic import BaseModel

from src.utils.ids import new_project_id
from src.services.storage.project_store import create_project, load_project

router = APIRouter()

class CreateProjectReq(BaseModel):
    user_input: str

@router.post("")
def create(req: CreateProjectReq):
    pid = new_project_id()
    state = create_project(pid, req.user_input)
    return state.model_dump()

@router.get("/{project_id}")
def get(project_id: str):
    state = load_project(project_id)
    if not state:
        return {"error": "project not found"}
    return state.model_dump()
