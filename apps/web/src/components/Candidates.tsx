// apps/web/src/components/Candidates.tsx
"use client";
import React from "react";
import { Candidate, Section } from "../lib/types";

const label: Record<Section, string> = {
  introduction: "서론",
  dataset: "데이터셋",
  method: "방법",
  conclusion: "결론",
};

export default function Candidates({
  section,
  candidates,
  onSelect,
  busy,
}: {
  section: Section;
  candidates: Candidate[];
  onSelect: (candidateId: string) => void;
  busy: boolean;
}) {
  return (
    <div className="card">
      <h3>현재 단계: {label[section]} (후보 3개)</h3>
      {candidates.length === 0 ? (
        <small>아직 후보가 없습니다. ‘생성’을 눌러 후보를 만들거나, 이전 선택을 진행하세요.</small>
      ) : (
        candidates.map((c) => (
          <div key={c.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <small><b>{c.id}</b></small>
              <button disabled={busy} onClick={() => onSelect(c.id)}>이 후보 선택</button>
            </div>
            <pre>{c.text}</pre>
          </div>
        ))
      )}
    </div>
  );
}
