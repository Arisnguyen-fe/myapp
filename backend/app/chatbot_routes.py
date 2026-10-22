import os
from typing import List, Literal

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

load_dotenv(".env")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    text: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    # Cap history size so the public endpoint can't be used to burn API quota
    messages: List[ChatMessage] = Field(min_length=1, max_length=30)


class ChatResponse(BaseModel):
    reply: str


async def ask_gemini(messages: List[ChatMessage]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Chatbot is not configured")

    payload = {
        "contents": [{"role": m.role, "parts": [{"text": m.text}]} for m in messages]
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Send the key in a header, never in the URL, so it doesn't end up in logs
            response = await client.post(
                GEMINI_URL, json=payload, headers={"x-goog-api-key": api_key}
            )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        raise HTTPException(status_code=502, detail="Chatbot is unavailable right now")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    reply = await ask_gemini(request.messages)
    return ChatResponse(reply=reply.strip())
