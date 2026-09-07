from .intents import detect_intent
from .prompt_builder import PromptBuilder


class Router:

    @staticmethod
    def route(message: str):

        intent = detect_intent(message)

        context = PromptBuilder.build(message)

        return intent, context