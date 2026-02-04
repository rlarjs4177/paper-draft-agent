# apps/api/src/routes/select.py
from fastapi import APIRouter
from pydantic import BaseModel

from src.services.storage.project_store import load_project, save_project
from src.services.agent.orchestrator import set_selected, next_section

router = APIRouter()

class SelectReq(BaseModel):
    section: str
    candidate_id: str

@router.post("/{project_id}/select")
def select(project_id: str, req: SelectReq):
    state = load_project(project_id)
    if not state:
        return {"error": "project not found"}

    if req.section != state.stage:
        return {"error": f"invalid section. current stage is '{state.stage}'"}

    selected_text = set_selected(state, req.section, req.candidate_id)
    if selected_text is None:
        return {"error": "candidate_id not found"}

    state.stage = next_section(state.stage)
    save_project(state)
    return state.model_dump()
