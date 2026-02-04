# apps/api/src/routes/generate.py
from fastapi import APIRouter, Query

from src.services.storage.project_store import load_project, save_project
from src.services.agent.orchestrator import get_selected_texts
from src.services.agent.prompt_builder import build_prompt
from src.services.retrieval.corpus_index import search_corpus
from src.services.llm.exaone_client import generate_3_candidates

from src.schemas.candidate import Candidate

router = APIRouter()


def _to_jsonable(obj):
    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(x) for x in obj]

    if hasattr(obj, "model_dump"):
        return _to_jsonable(obj.model_dump())

    if hasattr(obj, "dict"):
        return _to_jsonable(obj.dict())

    if hasattr(obj, "__dict__"):
        return {k: _to_jsonable(v) for k, v in obj.__dict__.items()}

    return {"value": str(obj)}


@router.post("/{project_id}/generate")
def generate(
    project_id: str,
    section: str = Query(..., description="introduction|dataset|method|conclusion"),
):
    state = load_project(project_id)
    if not state:
        return {"error": "project not found"}

    if section != state.stage:
        return {"error": f"invalid section. current stage is '{state.stage}'"}

    selected = get_selected_texts(state)

    query_seed = state.user_input
    if selected.get("introduction"):
        query_seed = selected["introduction"][:500] + " " + state.user_input[:500]

    hits = search_corpus(query_seed, top_k=5) 

    # ---- RAG 상태 표준화 (list 전용) ----
    rag_status = "unknown"
    rag_message = None

    if isinstance(hits, list) and len(hits) > 0 and isinstance(hits[0], dict) and "status" in hits[0]:
        # empty_corpus/no_hit/empty_query는 보통 hit 1개짜리로 반환됨
        first_status = hits[0].get("status")
        if first_status in ("empty_corpus", "no_hit", "empty_query"):
            rag_status = first_status
            rag_message = hits[0].get("message")
        else:
            # ok hit 리스트
            # ok가 1개 이상이면 hit로 정규화
            has_ok = any(isinstance(h, dict) and h.get("status") == "ok" for h in hits)
            rag_status = "hit" if has_ok else "no_hit"
            if rag_status == "no_hit":
                rag_message = "No retrieval result matched the current query."
    else:
        # 예외 케이스
        rag_status = "unknown"
        rag_message = "Unexpected retrieval response format."

    corpus_hits_payload = _to_jsonable(hits)

    prompt = build_prompt(
        section=section,
        user_input=state.user_input,
        selected_sections=selected,
        corpus_hits=hits,
    )

    texts = generate_3_candidates(section, prompt)

    candidates = [
        Candidate(id=f"{section}_1", text=texts[0]),
        Candidate(id=f"{section}_2", text=texts[1]),
        Candidate(id=f"{section}_3", text=texts[2]),
    ]

    # ---- state 저장 (프로젝트 JSON에 남김) ----
    state.sections[section].candidates = candidates  # type: ignore
    state.sections[section].corpus_hits = corpus_hits_payload  # type: ignore
    state.sections[section].rag_status = rag_status  # type: ignore
    state.sections[section].rag_message = rag_message  # type: ignore
    state.sections[section].rag_query = query_seed  # type: ignore

    save_project(state)

    return {
        "project_id": project_id,
        "section": section,
        "stage": state.stage,
        "candidates": [c.model_dump() for c in candidates],
        "corpus_hits": corpus_hits_payload,
        "rag_status": rag_status,
        "rag_message": rag_message,
        "rag_query": query_seed,
    }
