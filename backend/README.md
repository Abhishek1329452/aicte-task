Quick setup for backend

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in `SUPABASE_URL`, `SUPABASE_KEY`, and `WEBHOOK_URL`.

3. Create the `patient_sessions` table in Supabase using `migrations/create_patients.sql` (Supabase SQL editor).

4. Run the app:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

API

POST /chat
Body: `{ "message": "...", "session_id": "optional" }`
Returns: `{ "reply": "...", "session_id": "..." }`

Notes

- The flow implementation is a small LangGraph-style local orchestrator in `backend/app/flow.py`.
- The webhook will be sent only after `patient_name`, `patient_age`, and `patient_query` are collected.
- Supabase insertion uses the REST endpoint; ensure `SUPABASE_KEY` has write permissions.
