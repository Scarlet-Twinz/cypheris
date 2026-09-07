from ..query_registry import QueryRegistry


class EnterpriseRouter:

    DATABASE_KEYWORDS = (
        "company",
        "companies",
        "organization",
        "organizations",
        "user",
        "users",
        "threat",
        "threats",
        "alert",
        "alerts",
        "device",
        "devices",
        "network",
        "invoice",
        "invoices",
        "subscription",
        "subscriptions",
        "security score",
        "security health",
        "dashboard",
        "registered",
        "active users",
        "active company",
        "active companies",
        "inactive company",
        "inactive companies",
        "notification",
        "notifications",
        "audit",
        "billing",
        "posture",
    )

    @staticmethod
    def route(message: str):

        question = (message or "").strip()

        if not question:
            return {
                "plan": ["general"]
            }

        task = EnterpriseRouter.detect_task(question)

        return {
            "plan": [task]
        }

    @staticmethod
    def handle(message: str):

        question = (message or "").strip()

        if not question:
            return None

        lower_message = question.lower()

        if not any(
            keyword in lower_message
            for keyword in EnterpriseRouter.DATABASE_KEYWORDS
        ):
            return None

        try:

            return EnterpriseRouter.route(question)

        except Exception as error:

            print(
                f"LYROMI Enterprise Router Error: {error}"
            )

            return {
                "plan": ["general"]
            }

    @staticmethod
    def detect_task(question: str):

        q = question.lower().strip()

        # =========================================================
        # COMPANIES
        # =========================================================

        if (
            "how many companies" in q
            or "number of companies" in q
            or "count companies" in q
            or "company count" in q
        ):
            return "company_count"

        if (
            "list all companies" in q
            or "show all companies" in q
            or "which companies" in q
            or "list companies" in q
        ):
            return "company_list"

        if (
            "active companies" in q
            or "active company" in q
            or "which companies are active" in q
            or "which company is active" in q
            or "show active companies" in q
            or "list active companies" in q
        ):
            return "active_company_list"

        if (
            "inactive companies" in q
            or "inactive company" in q
            or "which companies are inactive" in q
            or "show inactive companies" in q
            or "list inactive companies" in q
        ):
            return "inactive_company_count"

        # =========================================================
        # USERS
        # =========================================================

        if (
            "how many users" in q
            or "number of users" in q
            or "count users" in q
            or "user count" in q
        ):
            return "user_count"

        if (
            "list all users" in q
            or "show all users" in q
            or "which users" in q
            or "list users" in q
        ):
            return "user_list"

        if (
            "active users" in q
            or "how many active users" in q
        ):
            return "active_user_count"

        if (
            "inactive users" in q
            or "how many inactive users" in q
        ):
            return "inactive_user_count"

        if (
            "how many admins" in q
            or "number of admins" in q
            or "admin count" in q
        ):
            return "admin_count"

        # =========================================================
        # THREATS
        # =========================================================

        if (
            "how many threats" in q
            or "number of threats" in q
            or "count threats" in q
            or "threat count" in q
        ):
            return "active_threat_count"

        if "critical threats" in q:
            return "critical_threat_count"

        if "high threats" in q:
            return "high_threat_count"

        if (
            "active threats" in q
            or "open threats" in q
        ):
            return "active_threat_count"

        if (
            "recent threats" in q
            or "latest threats" in q
        ):
            return "recent_threats"

        # =========================================================
        # ALERTS
        # =========================================================

        if (
            "how many alerts" in q
            or "number of alerts" in q
            or "count alerts" in q
            or "alert count" in q
        ):
            return "alert_count"

        if "critical alerts" in q:
            return "critical_alert_count"

        if (
            "active alerts" in q
            or "open alerts" in q
        ):
            return "active_alert_count"

        # =========================================================
        # SECURITY / DASHBOARD
        # =========================================================

        if (
            "security score" in q
            or "security health" in q
            or "organization health" in q
            or "security posture" in q
        ):
            return "security_posture"

        if "dashboard" in q:
            return "dashboard_summary"

        # =========================================================
        # NETWORK
        # =========================================================

        if (
            "network summary" in q
            or "network statistics" in q
            or "network traffic" in q
        ):
            return "network_summary"

        if "source ips" in q:
            return "top_source_ips"

        if "destination ips" in q:
            return "top_destination_ips"

        if "protocol statistics" in q:
            return "protocol_statistics"

        if (
            "recent network flows" in q
            or "latest network flows" in q
        ):
            return "recent_network_flows"

        # =========================================================
        # SUBSCRIPTIONS
        # =========================================================

        if (
            "subscriptions" in q
            or "subscription summary" in q
            or "billing" in q
        ):
            return "subscription_summary"

        if (
            "over limit" in q
            or "over the user limit" in q
        ):
            return "over_limit_companies"

        # =========================================================
        # NOTIFICATIONS
        # =========================================================

        if (
            "unread notifications" in q
            or "unread notification" in q
        ):
            return "unread_notification_count"

        if (
            "recent notifications" in q
            or "latest notifications" in q
        ):
            return "recent_notifications"

        # =========================================================
        # AUDIT
        # =========================================================

        if (
            "audit logs" in q
            or "recent audit" in q
        ):
            return "recent_audit_logs"

        # =========================================================
        # FALLBACK
        # =========================================================

        return "general"