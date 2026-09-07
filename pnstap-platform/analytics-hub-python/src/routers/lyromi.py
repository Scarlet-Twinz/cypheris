from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from services.lyromi import LyromiEngine
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
