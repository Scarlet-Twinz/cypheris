import re

from .task_executor import TaskExecutor
from .reasoning_engine import ReasoningEngine
from ..tools.database_tool import DatabaseTool


class ActionEngine:

    # =============================================================
    # TASK GROUPS
    # =============================================================

    COMPANY_TASKS = {
        "company_detail",
        "company_security_summary",
        "company_users",
        "company_threats",
        "company_alerts",
        "company_network_summary",
        "company_subscription",
    }

    USER_TASKS = {
        "user_company",
        "user_detail",
    }

    # =============================================================
    # MAIN EXECUTION
    # =============================================================

    @staticmethod
    def execute(
        question: str,
        plan,
        history=None
    ):

        enterprise_data = {}

        print("\n========== ACTION ENGINE ==========")
        print("PLAN:", plan)
        print("QUESTION:", question)

        for task in plan:

            if task == "general":
                continue

            print(f"\nRunning task: {task}")

            try:

                params = ()

                # -------------------------------------------------
                # COMPANY-SPECIFIC TASK
                # -------------------------------------------------

                if task in ActionEngine.COMPANY_TASKS:

                    company_name = (
                        ActionEngine.extract_company_name(
                            question
                        )
                    )

                    print(
                        "EXTRACTED COMPANY:",
                        company_name
                    )

                    # -------------------------------------------------
                    # IMPORTANT SECURITY RULE
                    #
                    # If the question refers to a specific company
                    # but that company does not exist in the database,
                    # DO NOT execute the query without parameters.
                    #
                    # This prevents:
                    #
                    # "How many users does Microsoft have?"
                    #
                    # from accidentally returning data belonging
                    # to another company.
                    # -------------------------------------------------

                    if (
                        ActionEngine.question_contains_company_reference(
                            question
                        )
                        and not company_name
                    ):

                        enterprise_data[task] = {
                            "not_found": True,
                            "message": (
                                "The requested company is not "
                                "present in the enterprise database."
                            )
                        }

                        print(
                            "COMPANY NOT FOUND IN DATABASE."
                        )

                        continue

                    if company_name:
                        params = (company_name,)

                # -------------------------------------------------
                # USER-SPECIFIC TASK
                # -------------------------------------------------

                elif task in ActionEngine.USER_TASKS:

                    user_name = (
                        ActionEngine.extract_user_name(
                            question
                        )
                    )

                    print(
                        "EXTRACTED USER:",
                        user_name
                    )

                    if (
                        ActionEngine.question_contains_user_reference(
                            question
                        )
                        and not user_name
                    ):

                        enterprise_data[task] = {
                            "not_found": True,
                            "message": (
                                "The requested user is not "
                                "present in the enterprise database."
                            )
                        }

                        print(
                            "USER NOT FOUND IN DATABASE."
                        )

                        continue

                    if user_name:
                        params = (user_name,)

                # -------------------------------------------------
                # EXECUTE TASK
                # -------------------------------------------------

                result = TaskExecutor.execute(
                    task=task,
                    question=question,
                    params=params
                )

                enterprise_data[task] = result

            except Exception as error:

                print(
                    f"ERROR while executing {task}: {error}"
                )

                enterprise_data[task] = {
                    "error": str(error)
                }

        print(
            "\n========== ENTERPRISE DATA =========="
        )

        print(enterprise_data)

        print(
            "=====================================\n"
        )

        return ReasoningEngine.analyze(
            question=question,
            plan=plan,
            enterprise_data=enterprise_data,
            history=history
        )

    # =============================================================
    # DATABASE COMPANY DISCOVERY
    # =============================================================

    @staticmethod
    def _get_company_names():

        sql = """
            SELECT company_name
            FROM companies
            WHERE company_name IS NOT NULL
            ORDER BY LENGTH(company_name) DESC;
        """

        rows = DatabaseTool.execute(sql)

        if not rows:
            return []

        names = []

        for row in rows:

            name = row.get("company_name")

            if name:
                cleaned = str(name).strip()

                if cleaned:
                    names.append(cleaned)

        return names

    # =============================================================
    # DATABASE USER DISCOVERY
    # =============================================================

    @staticmethod
    def _get_user_names():

        sql = """
            SELECT full_name
            FROM users
            WHERE full_name IS NOT NULL
            ORDER BY LENGTH(full_name) DESC;
        """

        rows = DatabaseTool.execute(sql)

        if not rows:
            return []

        names = []

        for row in rows:

            name = row.get("full_name")

            if name:
                cleaned = str(name).strip()

                if cleaned:
                    names.append(cleaned)

        return names

    # =============================================================
    # COMPANY NAME EXTRACTION
    # =============================================================

    @staticmethod
    def extract_company_name(question: str):

        text = (question or "").strip()

        if not text:
            return None

        companies = (
            ActionEngine._get_company_names()
        )

        if not companies:
            return None

        lowered = text.casefold()

        # ---------------------------------------------------------
        # FIRST:
        # Match an actual company from the database.
        #
        # Longest names are checked first because the database
        # already orders them by length.
        # ---------------------------------------------------------

        for company in companies:

            company_lower = company.casefold()

            pattern = (
                r"(?<!\w)"
                + re.escape(company_lower)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                lowered
            ):
                return company

        # ---------------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT guess a company name from natural language.
        #
        # We only return a company if it actually exists in the
        # database.
        #
        # This is what prevents:
        #
        # Microsoft -> Cypheris
        #
        # ---------------------------------------------------------

        return None

    # =============================================================
    # USER NAME EXTRACTION
    # =============================================================

    @staticmethod
    def extract_user_name(question: str):

        text = (question or "").strip()

        if not text:
            return None

        users = (
            ActionEngine._get_user_names()
        )

        if not users:
            return None

        lowered = text.casefold()

        # ---------------------------------------------------------
        # FIRST:
        # Match an actual user from the database.
        # ---------------------------------------------------------

        for user in users:

            user_lower = user.casefold()

            pattern = (
                r"(?<!\w)"
                + re.escape(user_lower)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                lowered
            ):
                return user

        # ---------------------------------------------------------
        # Never guess a user.
        # ---------------------------------------------------------

        return None

    # =============================================================
    # COMPANY REFERENCE DETECTION
    # =============================================================

    @staticmethod
    def question_contains_company_reference(
        question: str
    ):

        text = (question or "").casefold().strip()

        if not text:
            return False

        # ---------------------------------------------------------
        # Explicit company-oriented language.
        #
        # This does NOT contain any company names.
        # It simply identifies that the user is asking about a
        # particular company.
        # ---------------------------------------------------------

        patterns = [

            r"\bhow many users does\b",

            r"\busers does\b",

            r"\busers for\b",

            r"\busers in\b",

            r"\bwhat threats does\b",

            r"\bthreats does\b",

            r"\bwhat alerts does\b",

            r"\balerts does\b",

            r"\bwhat is .*subscription\b",

            r"\bsubscription of\b",

            r"\bsubscription for\b",

            r"\btell me about\b",

            r"\bgive me the details of\b",

            r"\binformation about\b",

            r"\bdetails of\b",

            r"\bwhere is\b",

            r"\bis .* active\b",
        ]

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            ):
                return True

        return False

    # =============================================================
    # USER REFERENCE DETECTION
    # =============================================================

    @staticmethod
    def question_contains_user_reference(
        question: str
    ):

        text = (question or "").casefold().strip()

        if not text:
            return False

        patterns = [

            r"\bwhich company does\b",

            r"\bwhat company does\b",

            r"\bwhich company is\b",

            r"\bwhat company is\b",

            r"\bwhere does\b",

            r"\btell me about user\b",
        ]

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            ):
                return True

        return False