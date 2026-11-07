"""Demonstration-only medical-information response engine.

No LLM, no RAG, no clinical validation, no patient record access, no storage.
Uses transparent, deterministic routing to prewritten educational examples.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

KB = json.loads((Path(__file__).parent / 'knowledge_base.json').read_text(encoding='utf-8'))

GENERAL_DISCLAIMER = {
    'en': "Educational prototype only. Not medically reviewed or tailored to your child. Confirm care decisions with your child's oncology team.",
    'de': "Nur ein Informationsprototyp. Nicht medizinisch geprüft und nicht auf Ihr Kind abgestimmt. Bitte besprechen Sie Behandlungsentscheidungen mit dem onkologischen Team Ihres Kindes.",
}
URGENT_RESPONSE = {
    'en': "I cannot assess urgent symptoms. If a child receiving cancer treatment has a fever, breathing difficulties, severe bleeding, a seizure, or another concerning new symptom, contact their treating oncology team immediately using their instructions. If there is immediate danger, call local emergency services. Do not rely on this demo for triage.",
    'de': "Ich kann akute Symptome nicht beurteilen. Wenn ein Kind während einer Krebsbehandlung Fieber, Atemnot, schwere Blutungen, einen Krampfanfall oder andere beunruhigende neue Beschwerden hat, kontaktieren Sie sofort das Behandlungsteam nach dessen Anweisungen. Bei unmittelbarer Lebensgefahr rufen Sie den örtlichen Notruf. Diese Demo ist keine Notfallberatung.",
}
CLARIFY_RESPONSE = {
    'en': "I want to understand your question without guessing. Do you mean a medical term you heard, an aspect of treatment, or a new symptom? If the child is unwell or you are concerned about a new symptom during cancer treatment, contact the treating team rather than waiting for this demo.",
    'de': "Ich möchte Ihre Frage verstehen, ohne zu raten. Geht es um einen medizinischen Begriff, eine Behandlung oder ein neues Symptom? Wenn es dem Kind während einer Krebsbehandlung nicht gut geht oder neue Beschwerden auftreten, kontaktieren Sie bitte das Behandlungsteam und warten Sie nicht auf diese Demo.",
}
PERSONALIZED_RESPONSE = {
    'en': "Choosing a treatment for an individual child requires their diagnosis, tests, treatment plan, and clinical judgment. This prototype has none of those details and cannot recommend a treatment. A useful question for the oncology team is: ‘What options are appropriate for my child, and why?’",
    'de': "Die Wahl einer Behandlung für ein bestimmtes Kind erfordert Diagnose, Untersuchungen, Behandlungsplan und ärztliche Einschätzung. Dieser Prototyp hat diese Informationen nicht und kann keine Behandlung empfehlen. Eine hilfreiche Frage an das Behandlungsteam lautet: „Welche Möglichkeiten kommen für mein Kind infrage und warum?“",
}
UNKNOWN_RESPONSE = {
    'en': "I don't have a prepared answer to this question in the small demonstration library. Could you ask about chemotherapy, side effects, or questions for your doctor? For anything specific to your child, please ask the oncology team.",
    'de': "In dieser kleinen Demo-Wissensbasis habe ich keine vorbereitete Antwort darauf. Sie können nach Chemotherapie, Nebenwirkungen oder Fragen für die Ärztin oder den Arzt fragen. Bitte wenden Sie sich bei individuellen Fragen an das Behandlungsteam.",
}

# Order matters: safety handling must be evaluated before any general topic match.
URGENT_PATTERNS = [
    r'\b(fever|high temperature|difficulty breathing|trouble breathing|can.t breathe|seizure|uncontrolled bleeding|heavy bleeding)\b',
    r'\b(fieber|atemnot|atemprobleme|krampfanfall|starke blutung|schwere blutung)\b',
]
PERSONAL_PATTERNS = [
    r'\b(which|what) (treatment|medicine|drug|chemotherapy) (is|would be) best (for|to) (my|our) child\b',
    r'\b(should (my|our) child (take|have|receive)|how much (medicine|chemotherapy) should)\b',
    r'\b(welche behandlung|welches medikament|was soll mein kind nehmen)\b',
]
CLARIFY_PATTERNS = [
    r'^(my child is sick|my kid is sick|my child feels bad|my child feels unwell|my child isn.t well|mein kind ist krank|meinem kind geht es schlecht)[.!? ]*$',
    r'^(i need help|help me|hilfe|ich brauche hilfe)[.!? ]*$',
]
INTENT_PATTERNS = [
    ('side_effects', r'\b(side effect|side effects|nausea|hair loss|nebenwirkung|nebenwirkungen|übelkeit|haarausfall)\b'),
    ('doctor_questions', r'\b(ask (the |my |our )?doctor|questions for (the |my |our )?doctor|questions.*appointment|arzt fragen|fragen.*arzt|beim arzt)\b'),
    ('chemotherapy', r'\b(chemotherapy|chemo|chemotherapie|zytostatika)\b'),
]

FOLLOW_UPS = {
    'en': {
        'chemotherapy': ["What are the side effects of chemotherapy?", "What questions should I ask my doctor?"],
        'side_effects': ["What questions should I ask my doctor?", "What is chemotherapy?"],
        'doctor_questions': ["What is chemotherapy?", "What are the side effects?"],
        'clarify': ["What is chemotherapy?", "What are the side effects?"],
    },
    'de': {
        'chemotherapy': ["Welche Nebenwirkungen hat Chemotherapie?", "Welche Fragen soll ich beim Arzt stellen?"],
        'side_effects': ["Welche Fragen soll ich beim Arzt stellen?", "Was ist Chemotherapie?"],
        'doctor_questions': ["Was ist Chemotherapie?", "Welche Nebenwirkungen gibt es?"],
        'clarify': ["Was ist Chemotherapie?", "Welche Nebenwirkungen gibt es?"],
    },
}


def _response(*, intent: str, answer: str, lang: str, audience: str, level: str,
              matched: bool = False, clinician: bool = False,
              source_title: str | None = None, source_url: str | None = None,
              response_type: str = 'educational', policy: str = 'Curated-demo-content') -> dict[str, Any]:
    return {
        'intent': intent,
        'answer': answer,
        'source_title': source_title,
        'source_url': source_url,
        'review_status': 'demo_not_clinically_reviewed',
        'needs_clinician': clinician,
        'matched': matched,
        'disclaimer': GENERAL_DISCLAIMER[lang],
        # additive: old /chat consumers can keep using previous fields unchanged
        'response_type': response_type,
        'applied_level': level,
        'audience': audience,
        'language': lang,
        'policy': policy,
        'suggested_questions': FOLLOW_UPS.get(lang, {}).get(intent, []),
        'pipeline': [
            {'stage': 'Input', 'detail': f'{audience.title()} · {lang.upper()} · {level.title()}'},
            {'stage': 'Safety', 'detail': policy},
            {'stage': 'Routing', 'detail': intent.replace('_', ' ').title()},
            {'stage': 'Evidence', 'detail': 'Reference link supplied; clinical review not completed' if source_url else 'No source attached'},
        ],
    }


def answer_question(question: str, language: str = 'en', audience: str = 'parent',
                    age: int | None = None, level: str = 'simple') -> dict[str, Any]:
    lang = language if language in ('en', 'de') else 'en'
    who = audience if audience in ('child', 'parent') else 'parent'
    applied_level = level if level in ('simple', 'standard', 'detailed') else 'simple'
    if who == 'child' and (age is None or age < 12):
        applied_level = 'simple'
    elif who == 'child' and applied_level == 'detailed':
        applied_level = 'standard'

    q = re.sub(r'\s+', ' ', question.strip().casefold())
    if any(re.search(p, q, re.IGNORECASE) for p in URGENT_PATTERNS):
        return _response(intent='urgent_caution', answer=URGENT_RESPONSE[lang], lang=lang,
                         audience=who, level=applied_level, clinician=True,
                         response_type='safety_escalation', policy='Urgent keyword escalation')
    if any(re.search(p, q, re.IGNORECASE) for p in PERSONAL_PATTERNS):
        return _response(intent='individual_treatment', answer=PERSONALIZED_RESPONSE[lang],
                         lang=lang, audience=who, level=applied_level, clinician=True,
                         response_type='clinical_boundary', policy='No individual treatment recommendation')
    if any(re.search(p, q, re.IGNORECASE) for p in CLARIFY_PATTERNS):
        return _response(intent='clarify', answer=CLARIFY_RESPONSE[lang], lang=lang,
                         audience=who, level=applied_level, clinician=True,
                         response_type='clarifying_question', policy='Ambiguous input → clarification')
    intent = next((name for name, pattern in INTENT_PATTERNS if re.search(pattern, q, re.IGNORECASE)), None)
    if intent is None:
        return _response(intent='unknown', answer=UNKNOWN_RESPONSE[lang], lang=lang,
                         audience=who, level=applied_level, clinician=True,
                         response_type='safe_fallback', policy='No grounded answer → abstain')
    item = KB[intent]
    return _response(intent=intent, answer=item['answers'][lang][applied_level],
                     lang=lang, audience=who, level=applied_level, matched=True,
                     source_title=item['source_title'], source_url=item['source_url'],
                     response_type='educational', policy='General information only')
