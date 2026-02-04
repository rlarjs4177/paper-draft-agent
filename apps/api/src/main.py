# apps/api/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.project import router as project_router
from src.routes.generate import router as generate_router
from src.routes.select import router as select_router

from src.services.llm.exaone_client import exaone_init  # 모델 로딩
from src.services.storage.corpus_store import corpus_init  # 코퍼스 로딩

app = FastAPI(title="Paper Draft Agent API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_router, prefix="/project", tags=["project"])
app.include_router(generate_router, prefix="/project", tags=["generate"])
app.include_router(select_router, prefix="/project", tags=["select"])

@app.on_event("startup")
def on_startup():
    # 서버 뜰 때 한번만 로딩
    corpus_init()
    exaone_init()

@app.get("/health")
def health():
    return {"ok": True}
