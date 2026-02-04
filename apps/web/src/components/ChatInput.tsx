// apps/web/src/components/ChatInput.tsx
"use client";
import React from "react";

export default function ChatInput({
  value,
  onChange,
  onGenerate,
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  onGenerate: () => void;
  disabled: boolean;
}) {
  return (
    <div className="card">
      <h3>구현한 연구 내용 입력</h3>
      <textarea
        placeholder="여기에 구현한 연구 내용을 입력하세요..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, marginTop: 10 }}>
        <small>입력 후 생성 버튼을 누르면 ‘서론’ 후보 3개가 생성됩니다.</small>
        <button onClick={onGenerate} disabled={disabled || !value.trim()}>
          생성
        </button>
      </div>
    </div>
  );
}
