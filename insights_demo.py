"""Synthetic-only analysis concept; no clinical inference or user-uploaded data."""
EXAMPLES = [
    {
        "id": "child_fatigue",
        "persona": "Child companion · synthetic example",
        "input_origin": "Pre-written fictional child message — NOT a patient record",
        "sample_text": "I feel very tired in the evening. I have not told the nurse yet.",
        "extracted_observations": [
            {"label": "Symptom mention", "value": "tiredness / fatigue", "evidence": "very tired"},
            {"label": "Time expression", "value": "evening", "evidence": "in the evening"},
            {"label": "Disclosure concern", "value": "hesitant to tell nurse", "evidence": "have not told the nurse yet"}
        ],
        "clinical_interpretation": "Not assessed; symptom severity and cause are unknown.",
        "suggested_workflow": "Encourage the child to seek support; any sharing requires appropriate authorization and a safeguarding policy.",
        "future_target": "Consent-controlled extraction → longitudinal symptom summary → clinician review",
    },
    {
        "id": "routine_trends",
        "persona": "Daily routine · synthetic example",
        "input_origin": "Fictional check-in entries supplied for demonstration",
        "sample_text": "Day 1: good appetite, mild tiredness; Day 2: less appetite, moderate tiredness; Day 3: less appetite, moderate tiredness.",
        "extracted_observations": [
            {"label": "Observed trend", "value": "reported appetite decreased", "evidence": "good → less → less"},
            {"label": "Observed trend", "value": "reported tiredness increased", "evidence": "mild → moderate → moderate"},
            {"label": "Inference boundary", "value": "cannot infer cancer stage or progression", "evidence": "self-reported routine alone"},
        ],
        "clinical_interpretation": "Descriptive trend only; no diagnosis or disease-stage prediction.",
        "suggested_workflow": "Only with permission: share a concise trend summary with a qualified clinician.",
        "future_target": "Longitudinal patient-reported outcomes with a validated pediatric framework",
    },
    {
        "id": "caregiver_topics",
        "persona": "Caregiver community · synthetic example",
        "input_origin": "Fictional caregiving message — NOT an analyzed dataset",
        "sample_text": "After treatment my child eats very little, and I don't know what to prepare for dinner.",
        "extracted_observations": [
            {"label": "Candidate topic", "value": "nutrition and appetite", "evidence": "eats very little"},
            {"label": "Care context", "value": "after treatment", "evidence": "After treatment"},
            {"label": "Support need", "value": "caregiver information and peer support", "evidence": "don't know what to prepare"},
        ],
        "clinical_interpretation": "A topic label only, not a recommended nutrition protocol.",
        "suggested_workflow": "Future: separate research consent, de-identification, cohort-level topic analysis and clinician validation.",
        "future_target": "Aggregate caregiver research insights and opt-in moderated community",
    },
]

def samples():
    return {"mode": "synthetic_rule_based_examples", "uses_llm": False,
            "uses_clinical_records": False, "stores_chats": False,
            "warning": "Fictional preset examples only; not a validated medical analysis or clinical triage system.",
            "cases": EXAMPLES}
