from datetime import datetime
import traceback

from .memory import memory
from .memory_manager import MemoryManager
from .persistent_memory import PersistentMemory

from .ollama import Ollama
from .prompts import SYSTEM_PROMPT

from .brain import Router
from .brain.intent_classifier import IntentClassifier
from .brain.enterprise_router import EnterpriseRouter
from .brain.action_engine import ActionEngine
from .brain.reflection_engine import ReflectionEngine


class LyromiEngine:

    @staticmethod
    def process(message: str):

        try:

            user_id = 1
            now = datetime.now()

            # -----------------------------------------
            # Permanent Memory
            # -----------------------------------------

            lower = message.lower()

            if "my name is" in lower:

                name = message.split("my name is", 1)[1].strip()

                if name:

                    PersistentMemory.save(
                        user_id=user_id,
                        key="name",
                        value=name
                    )

            # -----------------------------------------
            # Enterprise Requests
            # -----------------------------------------

            intent = IntentClassifier.classify(message)

            print("\n========== INTENT ==========")
            print(intent)

            if intent == "enterprise":

                enterprise = EnterpriseRouter.route(message)

                print("\n========== PLAN ==========")
                print(enterprise)

                reply = ActionEngine.execute(
                    question=message,
                    plan=enterprise["plan"]
                )

                memory.add("user", message)
                memory.add("assistant", reply)

                return reply

            # -----------------------------------------
            # Normal Conversation
            # -----------------------------------------

            intent_name, context = Router.route(message)
                 
            MemoryManager.remember(
                user_id=user_id,
                message=message
            )

            memory_context = MemoryManager.build_context(user_id)

            if len(memory_context) > 800:
                memory_context = memory_context[-800:]

            system_prompt = f"""
{SYSTEM_PROMPT}

Current Date:
{now.strftime('%A, %d %B %Y')}

Current Time:
{now.strftime('%I:%M %p')}

Detected Intent:
{intent_name}

Enterprise Context:
{context}

Known User Memory:
{memory_context}
"""

            memory.add("user", message)

            reply = Ollama.ask(
                system_prompt=system_prompt,
                message=message,
                history=memory.get_history()
            )

            reply = ReflectionEngine.reflect(
                question=message,
                answer=reply
            )

            memory.add("assistant", reply)

            return reply

        except Exception as e:

            print("\n========== FULL TRACEBACK ==========")
            traceback.print_exc()
            print("====================================\n")

            return f"LYROMI Error: {str(e)}"
