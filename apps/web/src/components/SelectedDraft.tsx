// apps/web/src/components/SelectedDraft.tsx
"use client";
import React from "react";
import { ProjectState, Section } from "../lib/types";

const order: Section[] = ["introduction", "dataset", "method", "conclusion"];
const label: Record<Section, string> = {
  introduction: "서론",
  dataset: "데이터셋",
  method: "방법",
  conclusion: "결론",
};

export default function SelectedDraft({ state }: { state: ProjectState | null }) {
  return (
    <div className="card">
      <h3>선택된 초안(누적)</h3>
      {!state ? (
        <small>프로젝트가 아직 없습니다.</small>
      ) : (
        order.map((sec) => (
          <div key={sec} className="card">
            <b>{label[sec]}</b>
            <pre>{state.sections[sec].selected_text ?? "(아직 선택되지 않음)"}</pre>
          </div>
        ))
      )}
    </div>
  );
}
