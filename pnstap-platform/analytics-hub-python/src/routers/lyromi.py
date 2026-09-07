from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from services.lyromi import LyromiEngine
from services.lyromi.ollama import Ollama
from auth import get_current_user

router = APIRouter(prefix="/api/lyromi", tags=["LYROMI"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


@router.post("/chat")
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    reply = LyromiEngine.process(
        request.message,
        user_id=current_user["user_id"],
        company_id=current_user["company_id"],
    )
    return {"reply": reply, "company_id": current_user["company_id"]}


@router.post("/stream")
def stream(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    context = LyromiEngine.build_context(
        user_id=current_user["user_id"],
        company_id=current_user["company_id"],
        message=request.message,
    )
    system_prompt = context.get("system_prompt", "You are LYROMI, the Cypheris security intelligence assistant.")
    enriched_message = context.get("message", request.message)

    return StreamingResponse(
        Ollama.stream(system_prompt, enriched_message),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
