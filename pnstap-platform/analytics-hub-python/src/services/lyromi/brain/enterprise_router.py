from .planner import Planner


class EnterpriseRouter:

    @staticmethod
    def route(message: str):

        plan = Planner.create_plan(message)

        return {
            "plan": plan
        }