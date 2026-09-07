from collections import deque
from datetime import datetime


class ConversationMemory:
    def __init__(self, max_messages: int = 20):
        self.history = deque(maxlen=max_messages)

    def add(self, role: str, content: str):
        self.history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
        )

    def get_history(self):
        return [
            {
                "role": item["role"],
                "content": item["content"]
            }
            for item in self.history
        ]

    def clear(self):
        self.history.clear()

    def last(self, n=5):
        return list(self.history)[-n:]


memory = ConversationMemory()