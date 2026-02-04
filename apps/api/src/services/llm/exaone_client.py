# apps/api/src/services/llm/exaone_client.py
import os
import re
import torch
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.utils.logger import logger

load_dotenv()

LLM_MODE = os.getenv("LLM_MODE", "local")  # local | stub
MODEL_ID = os.getenv("EXAONE_MODEL_ID", "LGAI-EXAONE/EXAONE-4.0-1.2B")
TORCH_DTYPE = os.getenv("TORCH_DTYPE", "bfloat16")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "10000"))

# 후보 품질 하한선 (참고용, 재시도는 하지 않음)
MIN_CANDIDATE_CHARS = int(os.getenv("MIN_CANDIDATE_CHARS", "250"))

_tokenizer = None
_model = None


def _resolve_dtype(name: str):
    name = name.lower().strip()
    if name == "bfloat16":
        return torch.bfloat16
    if name == "float16":
        return torch.float16
    return torch.float32


def exaone_init():
    global _tokenizer, _model
    if LLM_MODE == "stub":
        logger.info("LLM_MODE=stub (no model load)")
        return

    if _tokenizer is not None and _model is not None:
        return

    logger.info(f"Loading EXAONE model: {MODEL_ID} (dtype={TORCH_DTYPE})")
    dtype = _resolve_dtype(TORCH_DTYPE)

    # exaone4는 remote code 필요
    _tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        use_fast=False,
        trust_remote_code=True,
    )

    # pad_token 안전 세팅
    if _tokenizer.pad_token_id is None:
        if _tokenizer.eos_token_id is None and _tokenizer.bos_token_id is not None:
            _tokenizer.eos_token = _tokenizer.bos_token
        _tokenizer.pad_token = _tokenizer.eos_token

    _model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )
    _model.eval()
    logger.info("EXAONE model loaded.")


def _normalize(text: str) -> str:
    t = text.strip()
    t = t.replace("\r\n", "\n")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _is_bad_candidate(text: str) -> bool:
    """
    참고용 필터 (UI 판단/로그용)
    - 재시도는 하지 않음
    """
    t = text.strip()

    if len(t) < MIN_CANDIDATE_CHARS:
        return True

    if re.fullmatch(r"(#+\s*[^\n]+)\s*", t):
        return True

    lines = [x.strip() for x in t.splitlines() if x.strip()]
    if len(lines) <= 2 and lines[0].startswith("#"):
        return True

    return False


def _encode_prompt(prompt: str):
    assert _tokenizer is not None

    messages = [{"role": "user", "content": prompt}]
    enc = _tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    )

    if isinstance(enc, torch.Tensor):
        return enc, None

    return enc["input_ids"], enc.get("attention_mask", None)


def _generate_once(prompt: str, temperature: float) -> str:
    assert _model is not None and _tokenizer is not None

    input_ids, attention_mask = _encode_prompt(prompt)
    input_ids = input_ids.to(_model.device)
    if attention_mask is not None:
        attention_mask = attention_mask.to(_model.device)

    with torch.no_grad():
        out_ids = _model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=temperature,
            top_p=0.9,

            # 반복 억제 + 너무 빨리 끝나는 것 완화
            repetition_penalty=1.05,
            no_repeat_ngram_size=3,

            eos_token_id=_tokenizer.eos_token_id,
            pad_token_id=_tokenizer.pad_token_id,
        )

    gen = out_ids[0, input_ids.shape[1]:]
    text = _tokenizer.decode(gen, skip_special_tokens=True)
    return _normalize(text)


def generate_3_candidates(section: str, prompt: str) -> list[str]:
    """
    각 후보를 딱 1번만 생성 (retry 없음)
    - 속도 최우선
    - 품질 판단은 UI/사용자에게 위임
    """
    if LLM_MODE == "stub":
        base = f"{section} draft (stub): {prompt[:120]}..."
        return [
            base + "\n\n(candidate 1)",
            base + "\n\n(candidate 2)",
            base + "\n\n(candidate 3)",
        ]

    assert _tokenizer is not None and _model is not None

    temps = [0.3, 0.7, 0.95]
    outs: list[str] = []

    for idx, t in enumerate(temps, start=1):
        cand = _generate_once(prompt, temperature=t)

        if _is_bad_candidate(cand):
            logger.info(f"[LLM] candidate_{idx} flagged as low-quality (no retry)")

        outs.append(cand)

    return outs
