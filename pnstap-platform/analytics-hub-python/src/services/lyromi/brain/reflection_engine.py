class ReflectionEngine:

    @staticmethod
    def reflect(question: str, answer: str):

        if not answer:
            return answer

        text = answer.lower().strip()

        if "no data available" in text:
            return "I searched the enterprise database but couldn't find enough information to answer that question."

        # Only treat the answer as an error when it is clearly an error response.
        error_phrases = [
            "error occurred",
            "an error occurred",
            "internal server error",
            "failed to process",
            "exception occurred"
        ]

        if any(phrase in text for phrase in error_phrases):
            return "I encountered a problem while processing your request. Please try again."

        return answer