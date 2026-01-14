import re
import os
import httpx

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Simple keyword lists for routing
EMERGENCY_KEYWORDS = ["pain", "bleed", "bleeding", "chest", "unconscious", "emergency", "severe", "urgent", "fracture"]
MENTAL_KEYWORDS = ["depress", "depression", "anxious", "anxiety", "suicide", "mental", "therapy", "psych", "panic", "hallucinat"]

# helper
def contains_keyword(text: str, keywords):
    t = text.lower()
    return any(k in t for k in keywords)

class FlowManager:
    """A minimal LangGraph-like flow manager implementing the requested nodes and clarification rules.

    Session state keys:
      ward: "general"|"emergency"|"mental_health"
      patient_name, patient_age, patient_query
      awaiting: one of 'patient_name','patient_age','patient_query' when asking for clarification
    """

    def __init__(self):
        self.sessions = {}

    def _classify_ward(self, text: str):
        if contains_keyword(text, EMERGENCY_KEYWORDS):
            return "emergency"
        if contains_keyword(text, MENTAL_KEYWORDS):
            return "mental_health"
        return "general"

    async def _trigger_webhook(self, record: dict):
        if not WEBHOOK_URL:
            return {"status": "webhook_skipped", "reason": "WEBHOOK_URL not configured"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(WEBHOOK_URL, json=record)
            resp.raise_for_status()
            return {"status": "webhook_sent", "code": resp.status_code}

    async def _persist_and_webhook(self, state: dict):
        # Insert into Supabase via supabase_client if available
        from .supabase_client import insert_patient_record
        record = {
            "patient_name": state.get("patient_name"),
            "patient_age": int(state.get("patient_age")) if state.get("patient_age") is not None else None,
            "patient_query": state.get("patient_query"),
            "ward": state.get("ward"),
        }
        await insert_patient_record(record)
        return await self._trigger_webhook(record)

    def _extract_age(self, text: str):
        # find a number for age (simple)
        m = re.search(r"(\d{1,3})", text)
        if m:
            val = int(m.group(1))
            if 0 < val < 150:
                return val
        return None

    def _maybe_fill_fields(self, state: dict, message: str):
        """Try to auto-fill fields from the user's message if present.
        Only fill fields that are missing.
        """
        if not state.get("patient_name"):
            # A heuristic: if message contains two words with capital letters, treat as name
            words = message.strip().split()
            if len(words) >= 2 and all(w[0].isupper() for w in words[:2]):
                state["patient_name"] = " ".join(words[:2])
        if not state.get("patient_age"):
            age = self._extract_age(message)
            if age:
                state["patient_age"] = age
        if not state.get("patient_query"):
            # If message longer than 10 chars, use it as query
            if len(message.strip()) > 10:
                state["patient_query"] = message.strip()

    async def process(self, session_id: str, message: str):
        """Main entry—acts like start_node -> router_node -> ward_node flow.

        Returns: (reply_text, new_state)
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "ward": None,
                "patient_name": None,
                "patient_age": None,
                "patient_query": None,
                "awaiting": None,
            }
        state = self.sessions[session_id]

        message = message.strip()

        # If we are currently awaiting a specific field, treat this message as the answer
        if state.get("awaiting"):
            field = state["awaiting"]
            # fill the field
            if field == "patient_age":
                age = self._extract_age(message)
                if age is None:
                    return ("I didn't catch the age—please provide the patient's age in years.", state)
                state["patient_age"] = age
            elif field == "patient_name":
                # accept the message as name
                state["patient_name"] = message.strip()
            elif field == "patient_query":
                state["patient_query"] = message.strip()
            state["awaiting"] = None

            # after filling, continue processing to either ask next or finish

        else:
            # start_node: accept message and maybe auto-fill some fields
            # Try to auto-fill some fields
            self._maybe_fill_fields(state, message)

            # router_node: classify if ward not set
            if not state.get("ward"):
                state["ward"] = self._classify_ward(message)

            # if still missing query and user message seems like a query, fill it
            if not state.get("patient_query") and len(message) > 10:
                state["patient_query"] = message

        # ward_node logic: collect missing fields one at a time
        # Do not assume details — ask one missing field at a time
        for field_name, prompt in [
            ("patient_name", "May I have the patient's full name, please?"),
            ("patient_age", "Could you provide the patient's age in years?"),
            ("patient_query", "Could you briefly describe the patient's concern or symptoms?"),
        ]:
            if not state.get(field_name):
                state["awaiting"] = field_name
                polite_prompt = f"""Thank you. {prompt}"""
                return (polite_prompt, state)

        # All fields present — persist and send webhook, then ack
        try:
            webhook_result = await self._persist_and_webhook(state)
        except Exception as e:
            return (f"All details collected, but there was an error submitting the data: {e}", state)

        # Clear session or mark completed
        self.sessions.pop(session_id, None)
        return ("Thank you — the patient's details have been recorded and sent to the ward.", {"completed": True, "webhook_result": webhook_result})
