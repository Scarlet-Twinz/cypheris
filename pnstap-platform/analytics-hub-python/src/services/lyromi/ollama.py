import json
import os
import urllib.error
import urllib.request


class Ollama:
    BASE_URL = os.getenv("OLLAMA_BASE_URL", os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
    MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")
    KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
    NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "192"))
    TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))

    @classmethod
    def _messages(cls, system_prompt, message, history=None):
        messages = [{"role": "system", "content": system_prompt}]
        for item in (history or [])[-6:]:
            if isinstance(item, dict) and item.get("role") in {"user", "assistant"}:
                messages.append({"role": item["role"], "content": str(item.get("content", ""))})
        messages.append({"role": "user", "content": message})
        return messages

    @classmethod
    def _payload(cls, system_prompt, message, history=None, stream=False):
        return {
            "model": cls.MODEL,
            "messages": cls._messages(system_prompt, message, history),
            "stream": stream,
            "keep_alive": cls.KEEP_ALIVE,
            "options": {
                "temperature": 0.2,
                "top_p": 0.85,
                "num_predict": cls.NUM_PREDICT,
                "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "4096")),
            },
        }

    @classmethod
    def ask(cls, system_prompt, message, history=None):
        request = urllib.request.Request(
            f"{cls.BASE_URL}/api/chat",
            data=json.dumps(cls._payload(system_prompt, message, history, stream=False)).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=cls.TIMEOUT) as response:
                result = json.loads(response.read().decode("utf-8"))
            return result.get("message", {}).get("content", "").strip() or "LYROMI returned no analysis."
        except urllib.error.URLError as error:
            print(f"LYROMI OLLAMA ERROR: {error}")
            return "LYROMI Error: The local AI service is unavailable."
        except Exception as error:
            print(f"LYROMI AI ERROR: {error}")
            return "LYROMI Error: I could not process that request."

    @classmethod
    def stream(cls, system_prompt, message, history=None):
        request = urllib.request.Request(
            f"{cls.BASE_URL}/api/chat",
            data=json.dumps(cls._payload(system_prompt, message, history, stream=True)).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=cls.TIMEOUT) as response:
                for raw_line in response:
                    if not raw_line.strip():
                        continue
                    try:
                        chunk = json.loads(raw_line.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
        except Exception as error:
            print(f"LYROMI STREAM ERROR: {error}")
            yield "LYROMI Error: The local AI service is unavailable."
