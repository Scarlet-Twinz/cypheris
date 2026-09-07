import json
import re

from ..ollama import Ollama


class Planner:

    # =============================================================
    # ALL LYROMI ENTERPRISE TASKS
    # =============================================================

    ALLOWED_PLANS = {
        "general",

        # Companies
        "company_count",
        "company_list",
        "company_detail",
        "active_company_list",
        "inactive_company_count",
        "company_user_count",
        "top_company_by_users",
        "company_security_summary",

        # Users
        "user_count",
        "user_list",
        "active_user_count",
        "inactive_user_count",
        "admin_count",
        "user_company",
        "user_detail",
        "company_users",

        # Threats
        "threat_count",
        "threat_list",
        "critical_threat_count",
        "high_threat_count",
        "active_threat_count",
        "recent_threats",
        "company_threats",

        # Alerts
        "alert_count",
        "critical_alert_count",
        "active_alert_count",
        "alert_list",
        "company_alerts",

        # Network
        "network_summary",
        "top_source_ips",
        "top_destination_ips",
        "protocol_statistics",
        "recent_network_flows",
        "company_network_summary",

        # Dashboard
        "dashboard_summary",
        "security_posture",
        "report",

        # Subscriptions
        "subscription_summary",
        "company_subscription",
        "over_limit_companies",

        # Notifications
        "unread_notification_count",
        "recent_notifications",

        # Audit
        "recent_audit_logs",
    }

    # =============================================================
    # LLM PROMPT
    # =============================================================

    SYSTEM_PROMPT = """
You are LYROMI, the enterprise AI security analyst for Cypheris.

Your ONLY job is to classify an enterprise question.

Return ONLY JSON:

{"plan":["task_name"]}

Never return prose.

AVAILABLE TASKS:

COMPANIES:
company_count
company_list
company_detail
active_company_list
inactive_company_count
company_user_count
top_company_by_users
company_security_summary

USERS:
user_count
user_list
active_user_count
inactive_user_count
admin_count
user_company
user_detail
company_users

THREATS:
threat_count
threat_list
critical_threat_count
high_threat_count
active_threat_count
recent_threats
company_threats

ALERTS:
alert_count
critical_alert_count
active_alert_count
alert_list
company_alerts

NETWORK:
network_summary
top_source_ips
top_destination_ips
protocol_statistics
recent_network_flows
company_network_summary

DASHBOARD:
dashboard_summary
security_posture
report

SUBSCRIPTIONS:
subscription_summary
company_subscription
over_limit_companies

NOTIFICATIONS:
unread_notification_count
recent_notifications

AUDIT:
recent_audit_logs

GENERAL:
general


IMPORTANT RULES:

Greetings:
hi
hello
hey
good morning
good afternoon
good evening
=> general


COMPANY COUNTS:

"how many companies do we have?"
"how many companies?"
"number of companies"
"count companies"
=> company_count


COMPANY LIST:

"list all companies"
"show all companies"
"which companies do we have?"
=> company_list


USERS:

"how many users?"
"how many users do we have?"
"number of users"
"count users"
=> user_count


THREATS:

"how many threats?"
"how many threats do we have?"
"number of threats"
"count threats"
"what is the number of threats?"
=> threat_count


"show threats"
"list threats"
"show all threats"
"list all threats"
=> threat_list


"recent threats"
"latest threats"
"show recent threats"
=> recent_threats


"how many critical threats?"
"number of critical threats"
=> critical_threat_count


"how many high threats?"
"number of high threats"
=> high_threat_count


"how many active threats?"
"number of active threats"
=> active_threat_count


COMPANY THREATS:

"what threats does Cypheris have?"
"what threats does Microsoft have?"
"show threats for Cypheris"
"show threats in Cypheris"
=> company_threats


ALERTS:

"how many alerts?"
"how many alerts do we have?"
"number of alerts"
=> alert_count


"how many critical alerts?"
=> critical_alert_count


"how many active alerts?"
=> active_alert_count


"show alerts"
"list alerts"
"recent alerts"
=> alert_list


COMPANY ALERTS:

"what alerts does Cypheris have?"
=> company_alerts


NETWORK:

"network summary"
"network activity"
"what is happening on the network?"
=> network_summary


"top source IPs"
=> top_source_ips


"top destination IPs"
=> top_destination_ips


"protocol statistics"
=> protocol_statistics


"recent network flows"
"network flows"
=> recent_network_flows


SECURITY:

"security posture"
"security status"
"security health"
=> security_posture


"dashboard summary"
"dashboard status"
"dashboard metrics"
=> dashboard_summary


"security report"
"generate a report"
"give me a report"
=> report


SUBSCRIPTIONS:

"subscription"
"subscriptions"
"billing"
=> subscription_summary


"subscription for Cypheris"
"subscription of Cypheris"
"what is Cypheris's subscription?"
=> company_subscription


"companies over their user limit"
=> over_limit_companies


NOTIFICATIONS:

"notifications"
"recent notifications"
=> recent_notifications


"unread notifications"
"how many unread notifications?"
=> unread_notification_count


AUDIT:

"audit logs"
"recent audit logs"
=> recent_audit_logs


GENERAL DEFINITIONS:

"what is a company?"
"what is a threat?"
"what is an alert?"
"what is a user?"
"what is cybersecurity?"
=> general


IMPORTANT:

Never invent enterprise data.

Never substitute one company for another.

The database determines whether a company exists.

Return JSON only.
"""

    # =============================================================
    # NORMALIZATION
    # =============================================================

    @staticmethod
    def normalize(message: str):

        return re.sub(
            r"\s+",
            " ",
            (message or "").strip().lower()
        ).strip()

    # =============================================================
    # DETERMINISTIC PLANNER
    # =============================================================

    @staticmethod
    def deterministic_plan(message: str):

        text = Planner.normalize(message)

        if not text:
            return ["general"]

        # ---------------------------------------------------------
        # GREETINGS
        # ---------------------------------------------------------

        greetings = {
            "hi",
            "hello",
            "hey",
            "yo",
            "good morning",
            "good afternoon",
            "good evening",
            "thanks",
            "thank you",
        }

        if text in greetings:
            return ["general"]

        # =========================================================
        # COMPANY COUNT
        # =========================================================

        if (
            (
                "how many" in text
                or "number of" in text
                or "count" in text
            )
            and (
                "company" in text
                or "companies" in text
            )
            and "user" not in text
        ):

            if "inactive" in text:
                return ["inactive_company_count"]

            return ["company_count"]

        # =========================================================
        # COMPANY LIST
        # =========================================================

        if (
            (
                "list" in text
                or "show" in text
                or "which" in text
            )
            and (
                "companies" in text
                or "company" in text
            )
        ):

            if "active" in text:
                return ["active_company_list"]

            return ["company_list"]

        # =========================================================
        # COMPANY USERS
        # =========================================================

        if (
            "how many users" in text
            and "each company" in text
        ):
            return ["company_user_count"]

        if (
            "which company has the most users" in text
            or "company with the most users" in text
            or "top company by users" in text
        ):
            return ["top_company_by_users"]

        if (
            "how many users does " in text
            and " have" in text
        ):
            return ["company_users"]

        if "users does " in text and " have" in text:
            return ["company_users"]

        if "users for " in text:
            return ["company_users"]

        if "users in " in text:
            return ["company_users"]

        # =========================================================
        # USER COUNTS
        # =========================================================

        if "how many users" in text or "number of users" in text:

            if "active" in text:
                return ["active_user_count"]

            if "inactive" in text:
                return ["inactive_user_count"]

            return ["user_count"]

        # =========================================================
        # ADMIN COUNT
        # =========================================================

        if (
            "how many admins" in text
            or "how many administrators" in text
            or "number of admins" in text
        ):
            return ["admin_count"]

        # =========================================================
        # USER LIST
        # =========================================================

        if (
            "list our users" in text
            or "list users" in text
            or "show users" in text
            or "who are our users" in text
        ):
            return ["user_list"]

        # =========================================================
        # USER -> COMPANY
        # =========================================================

        if (
            "which company does" in text
            and "belong" in text
        ):
            return ["user_company"]

        if (
            "what company does" in text
            and "belong" in text
        ):
            return ["user_company"]

        if (
            "where does" in text
            and "work" in text
        ):
            return ["user_company"]

        # =========================================================
        # THREAT COUNT
        #
        # THIS IS THE IMPORTANT FIX.
        # It MUST happen before generic "threats".
        # =========================================================

        if (
            (
                "how many" in text
                or "number of" in text
                or "count" in text
                or "total number" in text
            )
            and "threat" in text
        ):

            if "critical" in text:
                return ["critical_threat_count"]

            if "high" in text:
                return ["high_threat_count"]

            if "active" in text:
                return ["active_threat_count"]

            return ["threat_count"]

        # =========================================================
        # COMPANY THREATS
        # =========================================================

        if (
            "what threats does" in text
            or "threats does" in text
            or "threats for " in text
            or "threats in " in text
        ):
            return ["company_threats"]

        # =========================================================
        # THREAT LIST
        # =========================================================

        if (
            "recent threat" in text
            or "latest threat" in text
        ):
            return ["recent_threats"]

        if (
            "show threats" in text
            or "list threats" in text
            or "show all threats" in text
            or "list all threats" in text
        ):
            return ["threat_list"]

        # =========================================================
        # ALERT COUNT
        # =========================================================

        if (
            (
                "how many" in text
                or "number of" in text
                or "count" in text
            )
            and "alert" in text
        ):

            if "critical" in text:
                return ["critical_alert_count"]

            if "active" in text:
                return ["active_alert_count"]

            return ["alert_count"]

        # =========================================================
        # COMPANY ALERTS
        # =========================================================

        if (
            "what alerts does" in text
            or "alerts does" in text
            or "alerts for " in text
            or "alerts in " in text
        ):
            return ["company_alerts"]

        # =========================================================
        # ALERT LIST
        # =========================================================

        if (
            "show alerts" in text
            or "list alerts" in text
            or "recent alerts" in text
        ):
            return ["alert_list"]

        # =========================================================
        # SECURITY POSTURE
        # =========================================================

        if (
            "security posture" in text
            or "security status" in text
            or "security health" in text
        ):
            return ["security_posture"]

        # =========================================================
        # DASHBOARD
        # =========================================================

        if (
            "dashboard status" in text
            or "dashboard summary" in text
            or "dashboard metrics" in text
        ):
            return ["dashboard_summary"]

        # =========================================================
        # REPORT
        # =========================================================

        if (
            "security report" in text
            or "generate a report" in text
            or "give me a report" in text
        ):
            return ["report"]

        # =========================================================
        # NETWORK
        # =========================================================

        if (
            "what is happening on the network" in text
            or "network summary" in text
            or "network activity" in text
        ):
            return ["network_summary"]

        if "top source ip" in text:
            return ["top_source_ips"]

        if "top destination ip" in text:
            return ["top_destination_ips"]

        if "protocol statistics" in text:
            return ["protocol_statistics"]

        if (
            "recent network flows" in text
            or "network flows" in text
        ):
            return ["recent_network_flows"]

        # =========================================================
        # SUBSCRIPTIONS
        # =========================================================

        if "over their user limit" in text:
            return ["over_limit_companies"]

        if "subscription" in text or "billing" in text:

            if (
                "'s subscription" in text
                or "subscription for" in text
                or "subscription of" in text
                or "subscription plan for" in text
                or "subscription plan of" in text
            ):
                return ["company_subscription"]

            return ["subscription_summary"]

        # =========================================================
        # NOTIFICATIONS
        # =========================================================

        if "unread notification" in text:
            return ["unread_notification_count"]

        if "notification" in text:
            return ["recent_notifications"]

        # =========================================================
        # AUDIT
        # =========================================================

        if "audit log" in text:
            return ["recent_audit_logs"]

        # =========================================================
        # COMPANY DETAIL
        # =========================================================

        company_patterns = [
            r"^tell me everything about\s+.+$",
            r"^tell me about\s+.+$",
            r"^give me the details of\s+.+$",
            r"^details of\s+.+$",
            r"^information about\s+.+$",
            r"^where is\s+.+\s+located$",
            r"^is\s+.+\s+active$",
            r"^what is\s+.+$",
        ]

        general_definitions = {
            "what is a company",
            "what is a threat",
            "what is an alert",
            "what is a user",
            "what is an api key",
            "what is a password",
            "what is cybersecurity",
        }

        for pattern in company_patterns:

            if re.search(pattern, text):

                if text in general_definitions:
                    return ["general"]

                return ["company_detail"]

        # =========================================================
        # COMPANY KEYWORD
        # =========================================================

        if (
            "company" in text
            or "companies" in text
        ):
            return ["company_detail"]

        return None

    # =============================================================
    # LLM FALLBACK
    # =============================================================

    @staticmethod
    def create_plan(message: str):

        deterministic = Planner.deterministic_plan(message)

        if deterministic:

            print(
                "\nLYROMI DETERMINISTIC PLAN:",
                deterministic
            )

            return deterministic

        try:

            response = Ollama.ask(
                Planner.SYSTEM_PROMPT,
                message
            )

            response = response.strip()

            if response.startswith("```"):

                response = re.sub(
                    r"^```(?:json)?\s*",
                    "",
                    response,
                    flags=re.IGNORECASE
                )

                response = re.sub(
                    r"\s*```$",
                    "",
                    response
                )

            data = json.loads(response)

            plan = data.get("plan", [])

            if not isinstance(plan, list):
                return ["general"]

            clean_plan = [
                item
                for item in plan
                if item in Planner.ALLOWED_PLANS
            ]

            if not clean_plan:
                return ["general"]

            return clean_plan

        except Exception as error:

            print(
                f"\nLYROMI PLANNER ERROR: {error}"
            )

            return ["general"]