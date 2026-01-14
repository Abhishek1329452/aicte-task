import os
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .flow import FlowManager

app = FastAPI(title="Hospital Receptionist AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

flow = FlowManager()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    session_id = req.session_id or str(uuid.uuid4())
    reply, state = await flow.process(session_id, req.message)

    # If state is a dict with completed flag, reply produced by flow
    return {"reply": reply if isinstance(reply, str) else str(reply), "session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.app.main:app", host=os.getenv("HOST", "0.0.0.0"), port=port, reload=True)
