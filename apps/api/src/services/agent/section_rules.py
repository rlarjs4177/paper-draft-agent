# apps/api/src/services/agent/section_rules.py
SECTION_RULES = {
    "introduction": {
        "sentences": "100–120 sentences",
        "paragraphs": "5–8 paragraphs",
        "focus": [
            "Background and motivation for semiconductor process analytics and yield prediction",
            "Problem statement and practical constraints in manufacturing data",
            "Limitations of prior work (balanced, no overclaiming)",
            "Overview of the proposed approach and contributions",
            "Paper organization (optional if it improves clarity)",
        ],
    },
    "dataset": {
        "sentences": "70–100 sentences",
        "paragraphs": "4–7 paragraphs",
        "focus": [
            "Data source and collection scope (e.g., inline metrology; lot-level/wafer-level granularity)",
            "Target definition / labeling policy (only if explicitly stated by the user)",
            "Feature description and preprocessing (missing values, normalization, categorical encoding)",
            "Train/validation/test split strategy and leakage prevention considerations",
            "Data quality issues and assumptions (if applicable)",
        ],
    },
    "method": {
        "sentences": "200–300 sentences",
        "paragraphs": "6–10 paragraphs",
        "focus": [
            "End-to-end pipeline overview (step-by-step)",
            "Modeling/statistical approach and rationale",
            "How the method handles hierarchy (lot vs wafer) if relevant",
            "Evaluation protocol and metrics (conceptual; do not invent numbers)",
            "Implementation details relevant for reproducibility (high-level)",
        ],
    },
    "conclusion": {
        "sentences": "50–80 sentences",
        "paragraphs": "3–5 paragraphs",
        "focus": [
            "Concise summary of the work and main takeaways (no invented numbers)",
            "Practical implications for manufacturing decision-making",
            "Limitations and assumptions",
            "Future work directions",
        ],
    },
}
