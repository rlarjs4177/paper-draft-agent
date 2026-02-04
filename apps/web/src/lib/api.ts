// apps/web/src/lib/api.ts
import { Section, ProjectState } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function createProject(user_input: string): Promise<ProjectState> {
  const res = await fetch(`${API_BASE}/project`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_input }),
  });
  return await res.json();
}

export async function generateCandidates(project_id: string, section: Section) {
  const res = await fetch(`${API_BASE}/project/${project_id}/generate?section=${section}`, {
    method: "POST",
  });
  return await res.json();
}

export async function selectCandidate(project_id: string, section: Section, candidate_id: string): Promise<ProjectState> {
  const res = await fetch(`${API_BASE}/project/${project_id}/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ section, candidate_id }),
  });
  return await res.json();
}
