from datetime import datetime
import traceback

from .memory import memory
from .memory_manager import MemoryManager
from .ollama import Ollama
from .prompts import SYSTEM_PROMPT
from .brain import Router
from .brain.intent_classifier import IntentClassifier
from .brain.reflection_engine import ReflectionEngine
from .tenant_context import TenantContext


class LyromiEngine:
    """Tenant-aware LYROMI orchestration."""

    ENTERPRISE_HINTS = {
        "alert", "alerts", "asset", "assets", "identity", "identities", "investigation", "investigations",
        "evidence", "timeline", "drift", "sensor", "sensors", "integration", "integrations", "network",
        "security posture", "security status", "risk", "attack path", "workspace", "company", "organization",
        "users", "members", "threat", "threats", "what changed",
    }

    @staticmethod
    def _looks_enterprise(message: str, intent: str) -> bool:
        text = (message or "").casefold()
        return intent == "enterprise" or any(hint in text for hint in LyromiEngine.ENTERPRISE_HINTS)

    @staticmethod
    def build_context(user_id: int = 0, company_id: int = 0, message: str = ""):
        """Build the same tenant-grounded prompt used by chat, without invoking the model."""
        tenant_context = TenantContext.build(company_id) if company_id else {"available": False, "reason": "Workspace identity unavailable."}
        intent = IntentClassifier.classify(message)
        if LyromiEngine._looks_enterprise(message, intent):
            system_prompt = f"""
You are LYROMI, the contextual security intelligence layer for Cypheris.
The authenticated workspace context below is your ONLY source of enterprise truth.
Never invent, estimate, guess, or import facts from outside the context.
If the context does not contain enough evidence, say that clearly.
Keep counts exact. Distinguish zero from unavailable.
Do not reveal credentials, tokens, secrets, or private implementation details.
Answer the user's actual question first and stay concise.

AUTHENTICATED WORKSPACE CONTEXT:
{tenant_context}
"""
            return {"system_prompt": system_prompt, "message": message}

        _, context = Router.route(message)
        memory_context = MemoryManager.build_context(user_id)
        if len(memory_context) > 600:
            memory_context = memory_context[-600:]
        system_prompt = f"""
{SYSTEM_PROMPT}

Current Date: {datetime.now().strftime('%A, %d %B %Y')}
Detected Intent: {intent}

Known User Memory:
{memory_context}
"""
        return {"system_prompt": system_prompt, "message": message}

    @staticmethod
    def process(message: str, user_id: int = 0, company_id: int = 0):
        try:
            context = LyromiEngine.build_context(user_id=user_id, company_id=company_id, message=message)
            memory.add("user", message)
            reply = Ollama.ask(system_prompt=context["system_prompt"], message=context["message"], history=memory.get_history())
            reply = ReflectionEngine.reflect(question=message, answer=reply)
            memory.add("assistant", reply)
            return reply
        except Exception as error:
            print("LYROMI ERROR:", repr(error))
            traceback.print_exc()
            return "LYROMI Error: I could not process that request."
