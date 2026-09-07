import re


class MemoryExtractor:

    PATTERNS = [

        (r"my name is (.+)", "name"),
        (r"call me (.+)", "name"),

        (r"i am ([a-zA-Z ]+)$", "identity"),

        (r"my company is (.+)", "company"),

        (r"i live in (.+)", "location"),

        (r"my favorite language is (.+)", "favorite_language"),

        (r"my favorite color is (.+)", "favorite_color"),

        (r"i like (.+)", "likes"),

        (r"i dislike (.+)", "dislikes"),

        (r"i am building (.+)", "project"),

        (r"my project is (.+)", "project"),

        (r"i work as (.+)", "job"),

        (r"i study (.+)", "study"),

        (r"my school is (.+)", "school"),
    ]

    @staticmethod
    def extract(message: str):

        text = message.strip().lower()

        for pattern, key in MemoryExtractor.PATTERNS:

            match = re.search(pattern, text)

            if match:
                return key, match.group(1).strip()

        return None, None