# apps/api/src/services/agent/orchestrator.py
from typing import Dict, Optional
from src.schemas.project import ProjectState, SECTIONS

def next_section(current: str) -> str:
    idx = SECTIONS.index(current)
    if idx >= len(SECTIONS) - 1:
        return current
    return SECTIONS[idx + 1]

def get_selected_texts(state: ProjectState) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for sec in SECTIONS:
        ss = state.sections[sec]  # type: ignore
        if ss.selected_text:
            out[sec] = ss.selected_text
    return out

def set_selected(state: ProjectState, section: str, candidate_id: str) -> Optional[str]:
    ss = state.sections[section]  # type: ignore
    hit = None
    for c in ss.candidates:
        if c.id == candidate_id:
            hit = c.text
            break
    if hit is None:
        return None
    ss.selected_id = candidate_id
    ss.selected_text = hit
    return hit
