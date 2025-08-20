import os
from dotenv import load_dotenv
from typing import List, Literal, Dict, Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from global_limit import global_bucket
from pydantic import BaseModel, Field
from openai import OpenAI

load_dotenv()
client = OpenAI()

app = FastAPI(title="Rudebot API (local)")

# CORS for Streamlit on localhost:8501
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Role = Literal["system", "user", "assistant"]

class ChatMessage(BaseModel):
    role: Role
    content: str

class ChatIn(BaseModel):
    messages: List[ChatMessage] = Field(default_factory=list)
    model: str | None = None  # optionally override model per-call

class ChatOut(BaseModel):
    text: str
    model: str

async def global_rate_guard():
    retry_after = await global_bucket.allow()
    if retry_after is not None:
        # Return 429 and a Retry-After header
        raise HTTPException(
            status_code=429,
            detail="Global rate limit reached. Try again later.",
            headers={"Retry-After": f"{int(retry_after)}"},
        )

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/chat", response_model=ChatOut, dependencies=[Depends(global_rate_guard)])
def chat(inp: ChatIn):
    model_id = inp.model or os.getenv("OPENAI_FT_MODEL", "gpt-4.1-mini")

    # Safety: always include a short guardrail system as first message
    system_guard = {
        "role": "system",
        "content": (
            "You are Rudebot: curt, sarcastic, dismissive. No slurs, threats, or targeted harassment. "
            "Refuse illegal/unsafe requests rudely. Keep replies under ~15 words."
        ),
    }

    # Build input list for Responses API
    input_messages: List[Dict[str, Any]] = [system_guard] + [
        {"role": m.role, "content": m.content} for m in inp.messages
    ]

    resp = client.responses.create(
        model=model_id,
        input=input_messages,
    )
    return ChatOut(text=resp.output_text, model=model_id)
