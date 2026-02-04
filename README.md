📄 Paper-Draft-Agent

사실 기반(Hallucination-aware) 학술 논문 초안 생성을 지원하는
Human-in-the-loop 논문 작성 에이전트

📘 개요 (Overview)

본 저장소는 **이미 수행된 연구 결과를 기반으로 학술 논문 초안 작성을 지원하기 위한
논문 작성 보조 에이전트(Paper Draft Agent)**의 설계와 구현을 담고 있습니다.

본 에이전트의 목적은
논문을 자동으로 완성해 주는 도구가 아니라,

연구자가 이미 수행한 실험·분석·코드를 근거로,
과장 없이 검증 가능한 범위 내에서
학술 논문 형식의 문장을 작성할 수 있도록 지원하는 도구

를 제공하는 데 있습니다.

특히 본 프로젝트는 대규모 언어 모델(LLM)의 환각(hallucination)을 구조적으로 제한하고,
연구자가 모든 핵심 선택 과정에 직접 개입하는
Human-in-the-loop 기반 논문 작성 방식을 기본 철학으로 합니다.

🎯 설계 목표 (Design Goals)

본 논문 작성 에이전트는 다음과 같은 원칙을 따릅니다.

1. 사실 기반 작성 (Fact-grounded Writing)

코드, 실험 결과, 보고서, README 등 명시적으로 제공된 자료만을 근거로 사용합니다.

수행하지 않은 실험이나 분석을 생성하지 않습니다.

2. 환각 방지 구조 (Hallucination-aware Design)

섹션별 작성 규칙과 프롬프트 계약(prompt contract)을 통해
언어 모델의 자유도를 구조적으로 제한합니다.

논문에서 주장 가능한 범위와 금지 표현을 명확히 정의합니다.

3. Human-in-the-loop

모든 문장은 단일 결과가 아닌 후보(candidate) 형태로 생성됩니다.

최종 선택과 수정은 연구자가 직접 수행합니다.

4. 단계적 논문 작성 방식

생성(Generate), 선택(Select), 누적(Assemble)을 명확히 분리하여 설계하였습니다.

단일 실행으로 논문 전체를 자동 생성하지 않습니다.

🧠 시스템 아키텍처 개요

본 에이전트는 다음 네 개의 계층으로 구성되어 있습니다.

Frontend
섹션별 초안 후보 비교 및 선택을 위한 사용자 인터페이스

Backend
프로젝트 상태 관리 및 API 제공

Agent Core
논문 작성 로직 및 프롬프트 제어

Knowledge & Retrieval (RAG)
코퍼스 기반 정보 검색 및 근거 제한

각 계층은 독립적으로 설계되어 있으며,
특정 언어 모델이나 특정 데이터셋에 종속되지 않습니다.

🖥️ Frontend (사용자 인터페이스)
주요 역할

섹션별 초안 후보를 시각적으로 비교할 수 있도록 지원

사용자가 선택한 문단만을 누적

논문 작성 진행 상태 확인

특징

자동 완성이 아닌 선택 기반 편집 방식

섹션 단위 다중 후보 비교 UI 제공

🔧 Backend (상태 관리 및 API)
주요 역할

논문 작성 상태 관리
(선택된 문단, 완료된 섹션 등)

에이전트 요청 및 응답 처리

초안 버전 관리

특징

섹션 단위 상태를 고정하여 관리

이미 확정된 문단은 이후 생성 과정에 반영

🤖 Agent Core (논문 작성 로직)
1) 섹션 인지형 프롬프트 구성

(Section-aware Prompt Builder)

Introduction, Method, Result, Limitation 등
논문 섹션별로 상이한 작성 규칙 적용

허용 가능한 주장, 금지 표현, 분량 및 톤을 명시적으로 제한

2) 후보 기반 초안 생성

(Candidate-based Generation)

각 섹션에 대해 복수의 초안 후보 생성

단일 정답 문장을 생성하지 않음

3) 사용자 선택 단계

(Human Selection Layer)

연구자가 직접 초안을 선택

선택된 문단만 누적하여 다음 단계로 전달

📚 Knowledge & Retrieval (RAG)

본 에이전트는 외부 지식 환각을 방지하기 위해
Retrieval-Augmented Generation(RAG) 구조를 사용합니다.

구성 요소

논문 및 보고서 텍스트 코퍼스

질의–문단 유사도 기반 검색

상위 문단만 언어 모델 입력으로 전달

목적

사용자가 제공한 코퍼스 범위 내에서만 문장 생성

논문 맥락과 일관된 서술 지원

🚀 실행 방법 (How to Run)

본 에이전트는
코퍼스 준비 → 백엔드 실행 → 프론트엔드 실행 순서로 동작합니다.

1) 코퍼스 텍스트 준비
data/corpus/parsed/


위 경로 아래에 .txt 파일을 최소 1개 이상 추가해 주시기 바랍니다.

논문, 보고서, 실험 노트 등 자유 형식의 텍스트를 사용할 수 있습니다.

파일이 없는 경우에도 시스템은 실행되지만,
검색 결과는 *“히트 없음(No retrieval result)”*으로 표시됩니다.

2) 백엔드 실행
cd paper-draft-agent/apps/api
conda activate <가상환경이름>
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000


기본 접속 주소: http://localhost:8000

FastAPI 및 Uvicorn 기반

3) 프론트엔드 실행
cd paper-draft-agent/apps/web
npm install
npm run dev


React 기반 사용자 인터페이스

⚠️ 주의 사항

프론트엔드는 백엔드 실행 이후 시작해 주시기 바랍니다.

코퍼스 내용은 논문에서 주장 가능한 범위를 제한하므로,
입력 자료를 신중히 선택해 주시기 바랍니다.

본 에이전트는 자동 논문 작성 도구가 아니며,
최종 논문에 대한 책임은 연구자에게 있습니다.

🚫 본 에이전트의 제한 사항

논문을 한 번에 자동 완성하지 않습니다.

수행하지 않은 실험을 수행한 것처럼 작성하지 않습니다.

검증되지 않은 수치나 결과를 생성하지 않습니다.

연구자의 판단을 대체하지 않습니다.

📜 라이선스 (License)

본 프로젝트는 연구 및 실험 목적의 코드로 제공됩니다.
사용하시는 언어 모델 및 코퍼스 데이터의 라이선스를 반드시 확인해 주시기 바랍니다.

✍️ Author

김건
Fact-grounded academic writing agent design