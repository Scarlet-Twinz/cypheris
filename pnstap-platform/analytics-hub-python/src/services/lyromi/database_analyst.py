from .ollama import Ollama


class DatabaseAnalyst:

    @staticmethod
    def analyze(question: str, task: str, data):

        # ----------------------------
        # COMPANY COUNT
        # ----------------------------

        if task == "company_count":

            count = data.get("count", 0)

            return f"We currently have {count} compan{'y' if count == 1 else 'ies'} registered."

        # ----------------------------
        # USER COUNT
        # ----------------------------

        if task == "user_count":

            count = data.get("count", 0)

            return f"We currently have {count} user{'s' if count != 1 else ''}."

        # ----------------------------
        # COMPANY LIST
        # ----------------------------

        if task == "company_list":

            if not data:
                return "No companies found."

            lines = []

            for company in data:

                lines.append(
                    f"• {company['name']} ({company['country']}) - {company['status']}"
                )

            return "\n".join(lines)

        # ----------------------------
        # USER LIST
        # ----------------------------

        if task == "user_list":

            if not data:
                return "No users found."

            lines = []

            for user in data:

                lines.append(
                    f"• {user['name']} — {user['role']} ({user['status']})"
                )

            return "\n".join(lines)

        # ----------------------------
        # DASHBOARD
        # ----------------------------

        if task == "dashboard_summary":

            if not data:
                return "No dashboard information available."

            return f"""
Executive Security Summary

• Organization Health: {data.get('organization_health')}
• Threat Level: {data.get('threat_level')}
• CPU Usage: {data.get('cpu_usage')}%
• Memory Usage: {data.get('memory_usage')}%
• Disk Usage: {data.get('disk_usage')}%
""".strip()

        # ----------------------------
        # THREATS
        # ----------------------------

        if task == "threat_list":

            if not data:
                return "No active threats."

            lines = []

            for threat in data:

                lines.append(
                    f"• {threat['title']} ({threat['severity']}) - {threat['status']}"
                )

            return "\n".join(lines)

        # ----------------------------
        # AI ANALYSIS
        # ----------------------------

        prompt = f"""
You are LYROMI.

Answer ONLY using this enterprise data.

Question:

{question}

Enterprise Data:

{data}

Rules:

- Never generate SQL.
- Never say you cannot access the database.
- Never tell the user to check the dashboard.
- Use ONLY the enterprise data.
"""

        return Ollama.ask(
            system_prompt=prompt,
            message=question,
            history=[]
        )
