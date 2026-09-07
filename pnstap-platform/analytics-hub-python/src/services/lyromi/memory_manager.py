from .memory_db import MemoryDB
from .brain.extractor import MemoryExtractor


class MemoryManager:

    @staticmethod
    def remember(user_id: int, message: str):
        """
        Extract important information from a message
        and store/update it in the database.
        """

        key, value = MemoryExtractor.extract(message)

        if key and value:
            MemoryDB.save(
                user_id=user_id,
                key=key,
                value=value
            )

    @staticmethod
    def build_context(user_id: int) -> str:
        """
        Load every stored memory and convert it into
        context for the AI.
        """

        memories = MemoryDB.get_all(user_id)

        if not memories:
            return ""

        lines = []

        for memory in memories:
            lines.append(
                f"{memory['memory_key']}: {memory['memory_value']}"
            )

        return "\n".join(lines)