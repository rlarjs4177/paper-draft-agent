# apps/api/src/services/storage/corpus_store.py
import os
from typing import Dict, List
from dotenv import load_dotenv

from src.utils.logger import logger

load_dotenv()
CORPUS_DIR = os.getenv("CORPUS_DIR", "../../data/corpus/parsed")

_CORPUS: Dict[str, str] = {}

def corpus_init() -> None:
    global _CORPUS
    _CORPUS = {}

    if not os.path.isdir(CORPUS_DIR):
        logger.info(f"Corpus dir not found: {CORPUS_DIR} (OK for MVP)")
        return

    for fn in os.listdir(CORPUS_DIR):
        if not fn.lower().endswith(".txt"):
            continue
        path = os.path.join(CORPUS_DIR, fn)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                _CORPUS[fn] = f.read()
        except Exception:
            continue

    logger.info(f"Loaded corpus files: {len(_CORPUS)} from {CORPUS_DIR}")

def corpus_list() -> List[str]:
    return list(_CORPUS.keys())

def corpus_get(fn: str) -> str:
    return _CORPUS.get(fn, "")

def corpus_all() -> Dict[str, str]:
    return _CORPUS
