# apps/api/src/utils/ids.py
import uuid

def new_project_id() -> str:
    return "P" + uuid.uuid4().hex[:8]
