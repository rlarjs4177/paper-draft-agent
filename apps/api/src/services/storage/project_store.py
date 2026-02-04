# apps/api/src/services/storage/project_store.py
import os, json
from typing import Optional
from dotenv import load_dotenv

from src.schemas.project import ProjectState, SECTIONS
from src.schemas.section import SectionState

load_dotenv()

PROJECTS_DIR = os.getenv("PROJECTS_DIR", "../../data/projects")

def _pdir(project_id: str) -> str:
    return os.path.join(PROJECTS_DIR, project_id)

def _ppath(project_id: str) -> str:
    return os.path.join(_pdir(project_id), "project.json")

def create_project(project_id: str, user_input: str) -> ProjectState:
    os.makedirs(_pdir(project_id), exist_ok=True)
    state = ProjectState(
        project_id=project_id,
        user_input=user_input,
        stage="introduction",
        sections={s: SectionState() for s in SECTIONS},  # type: ignore
    )
    save_project(state)
    return state

def load_project(project_id: str) -> Optional[ProjectState]:
    path = _ppath(project_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ProjectState.model_validate(data)

def save_project(state: ProjectState) -> None:
    os.makedirs(_pdir(state.project_id), exist_ok=True)
    with open(_ppath(state.project_id), "w", encoding="utf-8") as f:
        json.dump(state.model_dump(), f, ensure_ascii=False, indent=2)
