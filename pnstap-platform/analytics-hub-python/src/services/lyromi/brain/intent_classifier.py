from .planner import Planner


class IntentClassifier:

    @staticmethod
    def classify(message: str):
        plan = Planner.create_plan(message)

        if plan == ['general']:
            return 'general'

        return 'enterprise'