from fastapi import APIRouter
from pydantic import BaseModel
from services.lyromi import LyromiEngine

router = APIRouter(
    prefix="/api/lyromi",
    tags=["LYROMI"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest):
    reply = LyromiEngine.process(request.message)

    # Convert dictionary results into text
    if isinstance(reply, dict):

        if "company_count" in reply:

            company_result = reply["company_count"]

            # Extract the actual count from:
            # {"count": 1}
            if isinstance(company_result, dict):
                count = company_result.get("count", 0)
            else:
                count = company_result

            # Handle singular/plural correctly
            if count == 1:
                reply = "You currently have 1 company."
            else:
                reply = f"You currently have {count} companies."

        else:
            reply = ", ".join(
                f"{key}: {value}"
                for key, value in reply.items()
            )

    return {
        "reply": reply
    }