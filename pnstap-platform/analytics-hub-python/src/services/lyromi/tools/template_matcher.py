from .sql_templates import SQLTemplates


class TemplateMatcher:

    @staticmethod
    def find(question: str):

        q = question.lower()

        if "how many companies" in q:
            return SQLTemplates.TEMPLATES["company_count"]

        if "how many users" in q:
            return SQLTemplates.TEMPLATES["user_count"]

        if "list all companies" in q:
            return SQLTemplates.TEMPLATES["list_companies"]

        if "list all users" in q:
            return SQLTemplates.TEMPLATES["list_users"]

        if "organization summary" in q or "summarize our organization" in q:
            return SQLTemplates.TEMPLATES["organization_summary"]

        if "security posture" in q:
            return SQLTemplates.TEMPLATES["security_posture"]

        if "executive security report" in q:
            return SQLTemplates.TEMPLATES["organization_summary"]

        if "recommendation" in q or "security recommendation" in q:
            return SQLTemplates.TEMPLATES["organization_summary"]

        return None