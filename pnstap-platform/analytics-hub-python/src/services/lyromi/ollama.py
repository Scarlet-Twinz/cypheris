import json
import os
import urllib.request
import urllib.error


class Ollama:
    BASE_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")

    @classmethod
    def ask(cls, system_prompt, message, history=None):
        history = history or []

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        for item in history[-10:]:
            if isinstance(item, dict) and item.get("role") in {"user", "assistant"}:
                messages.append({
                    "role": item["role"],
                    "content": str(item.get("content", ""))
                })

        messages.append({
            "role": "user",
            "content": message
        })

        payload = {
            "model": cls.MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9
            }
        }

        request = urllib.request.Request(
            f"{cls.BASE_URL}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))

            return result["message"]["content"].strip()

        except urllib.error.URLError as error:
            print(f"LYROMI OLLAMA ERROR: {error}")
            return "LYROMI Error: The local AI service is unavailable."

        except Exception as error:
            print(f"LYROMI AI ERROR: {error}")
            return "LYROMI Error: I could not process that request."