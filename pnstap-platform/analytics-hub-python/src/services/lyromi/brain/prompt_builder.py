from .skills import requires_enterprise_context


class PromptBuilder:

    @staticmethod
    def build(message: str):

        if not requires_enterprise_context(message):
            return ""

        return """
Enterprise Mode Enabled

The user is asking about enterprise data.

Use enterprise tools whenever available.
Never invent enterprise information.
If enterprise tools return data, trust them over the language model.
"""