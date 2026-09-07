class Formatter:

    @staticmethod
    def success(message):
        return {
            "status": "success",
            "reply": message
        }

    @staticmethod
    def error(message):
        return {
            "status": "error",
            "reply": message
        }

    @staticmethod
    def clean(text: str):
        return text.strip()