# AI4KOnCo Information Companion · Interactive Web App + API

**Purpose:** Health Hack Saar 2026 UX / chatbot-backend demonstration for the **Providing Information** workstream. This independent concept is designed to complement, not replace, the existing Pioneo app wireframes.

**Safety:** Hackathon demonstration only. **Not clinically reviewed, not for real patients, not a medical device.** Use invented questions and scenarios only. There is no LLM or RAG in this version. Medical text is illustrative and must not be treated as advice. Links point to public sources, but the answers have **not** undergone line-by-line medical verification.

## Run on Windows PowerShell

```powershell
cd "D:\\Meterials\\Study\\UdS\\jobs\\HealthAi\\ai4konco_showcase_app"
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Adapt the folder path to where you unzip the project. On another OS, use a shell in the extracted `ai4konco_showcase_app` folder.

Open **http://127.0.0.1:8000/app**. The old **http://127.0.0.1:8000/demo** also redirects to the new app.

API docs: **http://127.0.0.1:8000/docs**.

## What can the judges actually see?

| View | Real functionality | What it demonstrates |
| --- | --- | --- |
| Conversation studio | Live POST /chat, parent/child audience, age, EN/DE, depth, source links | Context-aware information UX |
| Decision trace | Real routing metadata from backend, with policy and provenance labels | Transparent logic, not mysterious "AI" |
| Questions for doctor | Temporary in-browser list; can be copied | Patient autonomy and preparation for consultation |
| Knowledge & evidence | Live /knowledge topics and reference links | Source visibility + transparent review state |
| Safety test lab | 6 actual live requests against /chat with expected-route comparison | Clarify, abstain, personalize boundary, urgent caution |
| Developer handoff | JSON examples, copy button, Swagger link | Ready for child's frontend integration |

**Important design nuance:** In the current demo, the medical response content is prewritten in `knowledge_base.json`. A topic-level public link is **not** proof of a medically approved answer. Review badge always says `demo_not_clinically_reviewed`. The urgent keyword filter is illustrative, not clinical triage.

## Stable integration API

The old API fields are unchanged. New UI-oriented fields are added, so a teammate can keep using the old contract.

`POST /chat`

```json
{
  "question": "What is chemotherapy?",
  "language": "en",
  "audience": "child",
  "age": 10,
  "level": "simple"
}
```

Response includes **original fields**: `intent`, `answer`, `source_title`, `source_url`, `review_status`, `needs_clinician`, `matched`, `disclaimer`.

Also includes **optional frontend fields**: `response_type`, `applied_level`, `audience`, `language`, `policy`, `suggested_questions`, and `pipeline`.

```javascript
const result = await fetch('http://127.0.0.1:8000/chat', {
  method: 'POST',
  headers: {'Content-Type':'application/json'},
  body: JSON.stringify({
    question: 'What is chemotherapy?',
    language: 'en', audience: 'child', age: 10, level: 'simple'
  })
}).then(r => r.json());

console.log(result.answer, result.source_url, result.needs_clinician);
```

Other endpoints: `GET /health`, `GET /capabilities`, `GET /knowledge`, `GET /scenarios`.

### Integration with teammate's UI

1. Frontend sends question + language + audience + age + level.
2. Backend returns text + provenance + safety flags.
3. Frontend renders the answer, displays the source/review status, and shows a medical-team referral for `needs_clinician: true`.
4. *Do not* use the independent in-tab "saved" prototype as real clinical sharing. Pioneo's QR/patient ID and secure sharing are separate flows requiring formal integration and permissions.

If frontend runs on another port, add its origin to `ALLOWED_ORIGINS`. If running on another laptop, `localhost` addresses each laptop separately; deploy to a trusted shared environment or run UI and API on the same laptop for the demo. Do not make this prototype public with patient data.

## How the backend works

`main.py` API routing → `engine.py` safety-first policy routing → `knowledge_base.json` prewritten reference-themed answers → JSON response.

Order: urgent-keyword caution → individual-treatment boundary → clarification for vague questions → selected topic answer → unsupported-question fallback.

For younger children (age below 12), the explanation is limited to `simple`. For ages 12+ the `detailed` level is capped at `standard`. This is an **illustrative design rule** and has not been validated by real pediatric users.

## Tests

```bash
python -m pytest -q
```

There are functional unit tests, HTTP contract tests and 6 interactive demonstration scenarios in Safety test lab. They test **code behavior only**; they do not prove patient safety or medical accuracy.

## Why this fits the official challenge

The official problem is to create transferable **UX/UI design principles and evaluation criteria** under emotional, cognitive and clinical constraints. This prototype showcases:

- **Progressive / adaptive disclosure**: adjustable explanation depth;
- **Visible provenance**: show sources, review status and the absence of clinical personalization;
- **Clarification before guessing**: an uninformative question results in clarification;
- **Escalation with boundaries**: no personalized treatment recommendation, clinician referral for potentially urgent phrases;
- **Interoperability**: frontend-friendly API for the separate child interface.

For a final pitch, show an answer at two levels, then a vague question, then a safety case, and conclude with /chat API integration. Describe as **a functional UX prototype with a rule-based response engine**, not an AI model or medical-grade triage system.

## Future improvements (not implemented)

Clinical content selection and review, formal source/claim verification, licensed RAG index and trained-generation evaluation, identity/role-based access control, secure persistence, child privacy decisions, clinical escalation protocols, accessibility and user testing with appropriate ethical oversight.


## Pitch edition (v0.3) additions

- Added **Clinical insights lab** with 3 prewritten, fictional examples (child symptom mention, daily-routine trend, caregiver topics); no actual ML analysis, no case data uploads, no clinical prediction.
- `GET /insights/examples` exposes those examples for the demo.
- Added `render.yaml` and `DEPLOY_TO_RENDER.md` so the same FastAPI app can be deployed to an approved Render workspace and accessed from the presenting teammate's computer.
- The current **memory/save** feature remains temporary in-browser question-list UI, NOT secure persistence. Chat history, opt-in research reuse, medical review and clinical permissions are **future requirements**, not completed.
