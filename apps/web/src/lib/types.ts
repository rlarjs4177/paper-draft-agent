// apps/web/src/lib/types.ts
export type Section = "introduction" | "dataset" | "method" | "conclusion";

export type Candidate = {
  id: string;
  text: string;
};

export type SectionState = {
  candidates: Candidate[];
  selected_id: string | null;
  selected_text: string | null;
};

export type ProjectState = {
  project_id: string;
  user_input: string;
  stage: Section;
  sections: Record<Section, SectionState>;
};
