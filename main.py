"""AI4KOnCo Information Companion — local hackathon demonstrator.

Run: python -m uvicorn main:app --reload
Public API contract remains POST /chat, fully backward-compatible at existing fields.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field

from engine import KB, answer_question
from insights_demo import samples as synthetic_insights

ROOT = Path(__file__).resolve().parent
app = FastAPI(
    title='AI4KOnCo · Information Companion API',
    version='0.3.0',
    description='Hackathon UX demonstrator. Rule-based answers; no LLM, medical validation, or clinical use.',
)
origins = [v.strip() for v in os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8501,http://127.0.0.1:8501'
).split(',') if v.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET','POST'],
                   allow_headers=['Content-Type'], allow_credentials=False)


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    language: Literal['en', 'de'] = 'en'
    audience: Literal['parent', 'child'] = 'parent'
    age: int | None = Field(default=None, ge=0, le=120)
    level: Literal['simple', 'standard', 'detailed'] = 'simple'


class PipelineStage(BaseModel):
    stage: str
    detail: str


class ChatResponse(BaseModel):
    # Fields maintained from v0.1
    intent: str
    answer: str
    source_title: str | None
    source_url: str | None
    review_status: str
    needs_clinician: bool
    matched: bool
    disclaimer: str
    # Additional fields for transparent UI and integration
    response_type: str
    applied_level: str
    audience: str
    language: str
    policy: str
    suggested_questions: list[str]
    pipeline: list[PipelineStage]


@app.get('/', include_in_schema=False)
def root():
    return RedirectResponse('/app', status_code=307)


@app.get('/app', include_in_schema=False)
def web_app():
    return FileResponse(ROOT / 'static' / 'index.html', media_type='text/html')


@app.get('/demo', include_in_schema=False)
def legacy_demo():
    return RedirectResponse('/app', status_code=307)


@app.get('/assets/{filename}', include_in_schema=False)
def assets(filename: Literal['styles.css', 'app.js']):
    media = 'text/css' if filename.endswith('.css') else 'application/javascript'
    return FileResponse(ROOT / 'static' / filename, media_type=media)


@app.get('/health')
def health():
    return {'status':'ok', 'mode':'rule_based_demo', 'medical_review':'not_completed', 'api_version':'0.3.0'}


@app.get('/capabilities')
def capabilities():
    return {
        'product':'AI4KOnCo Information Companion · Hackathon concept',
        'stage':'UX + API demonstrator, not a clinical product',
        'mode':'deterministic_rule_based', 'uses_llm':False, 'uses_rag':False,
        'languages':['en','de'], 'audiences':['parent','child'],
        'explanation_levels':['simple','standard','detailed'],
        'medical_review':'not_completed', 'patient_records_connected':False,
        'questions_persisted_on_server':False, 'chat_endpoint':'/chat',
        'synthetic_insights_endpoint':'/insights/examples', 'synthetic_only':True,
        'knowledge_topics':len(KB)
    }


@app.get('/knowledge')
def knowledge():
    return {'review_status':'demo_not_clinically_reviewed', 'topics':[
        {'id':k,'title':k.replace('_',' ').title(),'source_title':v['source_title'],
         'source_url':v['source_url'],'languages':['en','de'],
         'levels':['simple','standard','detailed']}
        for k,v in KB.items()
    ]}


@app.get('/scenarios')
def scenarios():
    return {'scenarios':[
        {'id':'general','title':'General medical information','question':'What is chemotherapy?',
         'expected_intent':'chemotherapy','expected_type':'educational'},
        {'id':'depth','title':'Side effects','question':'What are the side effects of chemotherapy?',
         'expected_intent':'side_effects','expected_type':'educational'},
        {'id':'clarify','title':'Ambiguous question','question':'My child is sick.',
         'expected_intent':'clarify','expected_type':'clarifying_question'},
        {'id':'boundary','title':'Individual treatment decision','question':'Which treatment is best for my child?',
         'expected_intent':'individual_treatment','expected_type':'clinical_boundary'},
        {'id':'urgent','title':'Potentially urgent symptoms','question':'My child has a fever during chemotherapy.',
         'expected_intent':'urgent_caution','expected_type':'safety_escalation'},
        {'id':'unknown','title':'Out-of-scope question','question':'Can you read my blood test results?',
         'expected_intent':'unknown','expected_type':'safe_fallback'},
    ]}


@app.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest):
    # No analytics, chat logging, patient data access, or persistent conversation.
    return answer_question(**request.model_dump())


@app.get('/insights/examples')
def insights_examples():
    """Prewritten fake cases only. No patient data or automatic classification."""
    return synthetic_insights()
