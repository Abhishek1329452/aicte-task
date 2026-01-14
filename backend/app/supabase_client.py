import os
import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def insert_patient_record(record: dict):
    """Insert a patient record into Supabase via the REST API.
    Expects `record` keys: patient_name, patient_age, patient_query, ward
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment")

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/patient_sessions"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=[record], headers=headers)
        resp.raise_for_status()
        return resp.json()
