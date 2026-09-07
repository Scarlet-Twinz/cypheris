import re

from .database_tool import DatabaseTool


class SQLExecutor:

    @staticmethod
    def execute(sql: str, params=None):

        if not sql or not sql.strip():
            raise Exception(
                "SQL query cannot be empty."
            )

        query = sql.strip()

        # =====================================================
        # REMOVE SQL COMMENTS FOR SECURITY VALIDATION
        # =====================================================

        normalized = re.sub(
            r"--.*?$",
            "",
            query,
            flags=re.MULTILINE
        )

        normalized = re.sub(
            r"/\*.*?\*/",
            "",
            normalized,
            flags=re.DOTALL
        )

        normalized = normalized.strip()

        if not normalized:
            raise Exception(
                "SQL query cannot be empty."
            )

        # =====================================================
        # ONLY SELECT QUERIES ARE ALLOWED
        # =====================================================

        if not re.match(
            r"^select\b",
            normalized,
            flags=re.IGNORECASE
        ):
            raise Exception(
                "Only SELECT queries are allowed."
            )

        # =====================================================
        # BLOCK DANGEROUS SQL COMMANDS
        # =====================================================

        forbidden = [
            "insert",
            "update",
            "delete",
            "drop",
            "alter",
            "truncate",
            "create",
            "grant",
            "revoke",
            "merge",
            "replace",
            "execute",
            "call",
        ]

        for keyword in forbidden:

            pattern = rf"\b{re.escape(keyword)}\b"

            if re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE
            ):
                raise Exception(
                    f"Blocked SQL command: {keyword}"
                )

        # =====================================================
        # BLOCK MULTIPLE STATEMENTS
        # =====================================================

        statements = [
            statement.strip()
            for statement in normalized.split(";")
            if statement.strip()
        ]

        if len(statements) > 1:
            raise Exception(
                "Multiple SQL statements are not allowed."
            )

        # =====================================================
        # EXECUTE ONLY AFTER ALL CHECKS PASS
        # =====================================================

        return DatabaseTool.execute(
            query=query,
            params=params
        )