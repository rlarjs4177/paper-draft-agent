# apps/api/src/services/retrieval/corpus_index.py
import re
from typing import List, Dict, Any, Tuple
from src.services.storage.corpus_store import corpus_all


def _tokenize(query: str) -> List[str]:
    return [w for w in query.lower().split() if len(w) >= 2]


def _score(text: str, query_tokens: List[str]) -> int:
    t = text.lower()
    return sum(t.count(w) for w in query_tokens)


def _remove_citations(s: str) -> str:
    # (Author, 2020), [12], (2020) 같은 인용 흔적 제거
    s = re.sub(r"\[[0-9,\s]+\]", "", s)
    s = re.sub(r"\([^)]*\d{4}[^)]*\)", "", s)
    return s


def _remove_numbers(s: str) -> str:
    # 숫자/퍼센트/단위 같은 강한 사실 힌트 제거
    s = re.sub(r"\b\d+(\.\d+)?\b", "", s)
    s = re.sub(r"%", "", s)
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()


def _looks_too_specific(s: str) -> bool:
    # 스타일 문장 선별 시 과도하게 구체적인 문장 제거
    low = s.lower()
    if re.search(r"\d", s):
        return True
    if any(k in low for k in ["accuracy", "f1", "auc", "mape", "rmse", "precision", "recall", "map@"]):
        return True
    if any(k in low for k in ["dataset", "benchmark", "hyperparameter", "learning rate", "epochs", "batch size"]):
        return True
    if any(k in low for k in ["we achieve", "we outperform", "significant improvement", "state-of-the-art"]):
        return True
    return False


def _split_sentences_with_spans(text: str) -> List[Dict[str, Any]]:
    """
    문장 분리 + (start_char, end_char) span 추적.
    아주 단순 규칙 기반(영문 논문 기준)이며, UI에서 '어디 부분인지' 표시하기 충분한 수준.
    """
    src = text.replace("\r\n", "\n")

    # 문장 후보 분리 (문장 끝 기호 뒤 공백/개행 기준)
    parts = re.split(r"(?<=[.!?])\s+", src)

    out: List[Dict[str, Any]] = []
    cursor = 0

    for p in parts:
        raw = p
        # 현재 cursor 위치부터 raw를 찾는다 (중복 문장 대응 위해 find 사용)
        idx = src.find(raw, cursor)
        if idx < 0:
            # fallback: 그냥 넘어가되 cursor를 유지
            continue

        start = idx
        end = idx + len(raw)
        cursor = end

        s = " ".join(raw.strip().split())
        if len(s) < 60:
            continue

        out.append({
            "text": s,
            "start_char": start,
            "end_char": end,
        })

    return out


def _split_sentences(text: str) -> List[str]:
    # 기존 함수 호환(필요 시)
    sents = _split_sentences_with_spans(text)
    return [d["text"] for d in sents]


def _style_sanitize(text: str) -> List[str]:
    # 텍스트에서 "스타일 참고용 문장"만 추려내기
    text = _remove_citations(text)
    sents = _split_sentences(text)

    cleaned: List[str] = []
    for s in sents:
        s2 = _remove_numbers(s)
        if not s2:
            continue
        if _looks_too_specific(s2):
            continue
        # 너무 긴 문장은 잘라서 안정화
        if len(s2) > 220:
            s2 = s2[:220].rstrip() + "..."
        cleaned.append(s2)

    # 중복 제거(간단)
    uniq: List[str] = []
    seen = set()
    for s in cleaned:
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(s)

    return uniq[:12]  # 한 파일에서 최대 12문장만 사용


def _best_evidence_snippet_with_spans(
    text: str, query_tokens: List[str], max_sentences: int = 3
) -> Dict[str, Any]:
    """
    근거(evidence) 용:
    - query와 가장 관련 있는 문장 max_sentences개
    - 문장 인덱스 + 문장 텍스트 + char span(start/end)
    - snippet(문장들을 합친 문자열) 제공
    """
    sents = _split_sentences_with_spans(text)
    if not sents:
        return {
            "sentences": [],
            "snippet": "",
            "sentence_indices": [],
            "sentence_spans": [],
            "span": None,  # 전체 snippet span
        }

    scored: List[Tuple[int, int]] = []  # (idx, score)
    for i, d in enumerate(sents):
        ss = _score(d["text"], query_tokens)
        if ss <= 0:
            continue
        scored.append((i, ss))

    if not scored:
        return {
            "sentences": [],
            "snippet": "",
            "sentence_indices": [],
            "sentence_spans": [],
            "span": None,
        }

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:max_sentences]

    indices = [i for (i, _) in top]
    sentences = [sents[i]["text"] for i in indices]
    spans = [(sents[i]["start_char"], sents[i]["end_char"]) for i in indices]

    snippet = " ".join(sentences)
    if len(snippet) > 600:
        snippet = snippet[:600].rstrip() + "..."

    # 전체 span은 선택 문장들의 최소/최대 범위로 잡음
    span = (min(s[0] for s in spans), max(s[1] for s in spans)) if spans else None

    return {
        "sentences": sentences,
        "snippet": snippet,
        "sentence_indices": indices,
        "sentence_spans": spans,
        "span": span,
    }


def search_corpus(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    returns: list of dict hits (항상 list)

    - 코퍼스 없음: empty_corpus 1개
    - 쿼리 너무 짧음: empty_query 1개
    - 매칭 없음: no_hit 1개
    - 정상 매칭: ok hit N개
    """
    data = corpus_all()

    if not data:
        return [{
            "status": "empty_corpus",
            "message": (
                "No corpus files found. Please add at least one .txt file under "
                "data/corpus/parsed/ to enable retrieval."
            ),
            "filename": None,
            "score": 0,
            "style_snippet": "",
            "evidence_snippet": "",
            "evidence_sentences": [],
            "evidence_sentence_indices": [],
            "evidence_sentence_spans": [],
            "evidence_span": None,
        }]

    q_tokens = _tokenize(query)
    if not q_tokens:
        return [{
            "status": "empty_query",
            "message": "Query is empty or too short to retrieve relevant passages.",
            "filename": None,
            "score": 0,
            "style_snippet": "",
            "evidence_snippet": "",
            "evidence_sentences": [],
            "evidence_sentence_indices": [],
            "evidence_sentence_spans": [],
            "evidence_span": None,
        }]

    hits: List[Dict[str, Any]] = []

    for fn, txt in data.items():
        file_score = _score(txt, q_tokens)
        if file_score <= 0:
            continue

        style_sents = _style_sanitize(txt)
        style_snip = " ".join(style_sents[:6]) if style_sents else ""

        evidence = _best_evidence_snippet_with_spans(txt, q_tokens, max_sentences=3)

        # 둘 다 없으면 제외
        if not style_snip and not evidence.get("snippet"):
            continue

        hits.append({
            "status": "ok",
            "message": None,
            "filename": fn,              
            "score": int(file_score),

            # 스타일/근거 스니펫
            "style_snippet": style_snip,
            "evidence_snippet": evidence.get("snippet", ""),

            # “어디 내용인지” 추적 가능한 메타
            "evidence_sentences": evidence.get("sentences", []),
            "evidence_sentence_indices": evidence.get("sentence_indices", []),
            "evidence_sentence_spans": evidence.get("sentence_spans", []),  # [(start,end),...]
            "evidence_span": evidence.get("span", None),                    # (start,end)
        })

    hits.sort(key=lambda x: x["score"], reverse=True)

    if not hits:
        return [{
            "status": "no_hit",
            "message": "No retrieval result matched the current query.",
            "filename": None,
            "score": 0,
            "style_snippet": "",
            "evidence_snippet": "",
            "evidence_sentences": [],
            "evidence_sentence_indices": [],
            "evidence_sentence_spans": [],
            "evidence_span": None,
        }]

    return hits[:top_k]
