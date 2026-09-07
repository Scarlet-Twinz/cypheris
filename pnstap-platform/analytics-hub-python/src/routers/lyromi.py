from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from services.lyromi import LyromiEngine
from auth import get_current_user

router = APIRouter(prefix="/api/lyromi", tags=["LYROMI"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


@router.post("/chat")
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    # The workspace identity is authenticated here before LYROMI is invoked.
    reply = LyromiEngine.process(request.message)

    if isinstance(reply, dict):
        if "company_count" in reply:
            company_result = reply["company_count"]
            count = company_result.get("count", 0) if isinstance(company_result, dict) else company_result
            reply = f"You currently have {count} {'company' if count == 1 else 'companies'}."
        else:
            reply = ", ".join(f"{key}: {value}" for key, value in reply.items())

    return {"reply": reply, "company_id": current_user["company_id"]}
