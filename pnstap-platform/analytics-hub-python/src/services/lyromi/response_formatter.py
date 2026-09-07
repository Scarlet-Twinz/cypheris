class ResponseFormatter:

    @staticmethod
    def format(question: str, sql_result):

        if not sql_result:
            return "I couldn't find any matching data."

        q = question.lower()

        if "how many compan" in q:
            return f"There are currently {sql_result[0]['count']} companies registered."

        if "how many user" in q:
            return f"There are currently {sql_result[0]['count']} active users."

        if "list all compan" in q:

            lines = []

            for company in sql_result:

                lines.append(
                    f"• {company['company_name']} ({company['country']}) - {company['status']}"
                )

            return "\n".join(lines)

        if "list all user" in q:

            lines = []

            for user in sql_result:

                lines.append(
                    f"• {user['full_name']} — {user['role']} ({user['status']})"
                )

            return "\n".join(lines)

        return str(sql_result)