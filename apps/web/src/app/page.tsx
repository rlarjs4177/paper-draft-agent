// apps/web/src/app/page.tsx
"use client";

import React, { useMemo, useState } from "react";
import ChatInput from "../components/ChatInput";
import Candidates from "../components/Candidates";
import SelectedDraft from "../components/SelectedDraft";
import { createProject, generateCandidates, selectCandidate } from "../lib/api";
import { ProjectState, Section } from "../lib/types";

export default function Page() {
  const [input, setInput] = useState("");
  const [project, setProject] = useState<ProjectState | null>(null);
  const [busy, setBusy] = useState(false);

  const currentStage: Section = useMemo(() => (project ? project.stage : "introduction"), [project]);
  const currentCandidates = useMemo(() => {
    if (!project) return [];
    return project.sections[currentStage].candidates ?? [];
  }, [project, currentStage]);

  async function generateCurrentStage() {
    if (!project) return;

    const gen = await generateCandidates(project.project_id, project.stage);
    if (gen?.error) {
      alert(gen.error);
      return;
    }

    setProject((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        sections: {
          ...prev.sections,
          [prev.stage]: {
            ...prev.sections[prev.stage],
            candidates: gen.candidates ?? [],
          },
        },
      };
    });
  }

  async function onGenerate() {
    setBusy(true);
    try {
      if (!project) {
        const p = await createProject(input.trim());
        if ((p as any)?.error) {
          alert((p as any).error);
          return;
        }
        setProject(p);

        // 생성 버튼 눌렀을 때 서론 후보 바로 생성
        const gen = await generateCandidates(p.project_id, p.stage);
        if (gen?.error) {
          alert(gen.error);
          return;
        }
        setProject({
          ...p,
          sections: {
            ...p.sections,
            [p.stage]: { ...p.sections[p.stage], candidates: gen.candidates ?? [] },
          },
        });
      } else {
        await generateCurrentStage();
      }
    } finally {
      setBusy(false);
    }
  }

  async function onSelect(candidateId: string) {
    if (!project) return;
    setBusy(true);
    try {
      const updated = await selectCandidate(project.project_id, project.stage, candidateId);
      if ((updated as any)?.error) {
        alert((updated as any).error);
        return;
      }
      setProject(updated);

      // UX: 선택 후 다음 단계 후보도 자동 생성
      const gen = await generateCandidates(updated.project_id, updated.stage);
      if (gen?.error) return;

      setProject({
        ...updated,
        sections: {
          ...updated.sections,
          [updated.stage]: { ...updated.sections[updated.stage], candidates: gen.candidates ?? [] },
        },
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>Paper Draft Agent (서론 → 데이터셋 → 방법 → 결론)</h1>

      <div className="row">
        <div className="col">
          <ChatInput value={input} onChange={setInput} onGenerate={onGenerate} disabled={busy} />
          <Candidates section={currentStage} candidates={currentCandidates} onSelect={onSelect} busy={busy} />
        </div>

        <div className="col">
          <SelectedDraft state={project} />
          {project && (
            <div className="card">
              <small><b>project_id:</b> {project.project_id}</small><br />
              <small><b>stage:</b> {project.stage}</small>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
