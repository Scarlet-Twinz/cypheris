class EnterpriseFormatter:

    @staticmethod
    def _row_value(row, key, index=0, default=None):

        if isinstance(row, dict):
            return row.get(key, default)

        try:
            return row[index]
        except (IndexError, KeyError, TypeError):
            return default

    @staticmethod
    def _rows(rows):
        return rows or []

    @staticmethod
    def format(task: str, rows):

        if rows is None:
            return None

        rows = EnterpriseFormatter._rows(rows)

        # =========================================================
        # COUNT TASKS
        # =========================================================

        count_tasks = {
            "company_count": "company_count",
            "user_count": "user_count",

            "active_user_count": "active_user_count",
            "inactive_user_count": "inactive_user_count",
            "admin_count": "admin_count",

            "inactive_company_count": "inactive_company_count",

            # IMPORTANT
            "threat_count": "threat_count",

            "critical_threat_count": "critical_threat_count",
            "high_threat_count": "high_threat_count",
            "active_threat_count": "active_threat_count",

            "alert_count": "alert_count",
            "critical_alert_count": "critical_alert_count",
            "active_alert_count": "active_alert_count",

            "unread_notification_count":
                "unread_notification_count",
        }

        if task in count_tasks:

            key = count_tasks[task]

            if not rows:
                return {
                    "count": 0
                }

            return {
                "count": EnterpriseFormatter._row_value(
                    rows[0],
                    key,
                    0,
                    0
                )
            }

        # =========================================================
        # COMPANY LIST
        # =========================================================

        if task in {
            "company_list",
            "active_company_list"
        }:

            result = []

            for row in rows:

                result.append({
                    "name":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_name",
                            0
                        ),

                    "industry":
                        EnterpriseFormatter._row_value(
                            row,
                            "industry",
                            1
                        ),

                    "country":
                        EnterpriseFormatter._row_value(
                            row,
                            "country",
                            2
                        ),

                    "subscription_plan":
                        EnterpriseFormatter._row_value(
                            row,
                            "subscription_plan",
                            3
                        ),

                    "status":
                        EnterpriseFormatter._row_value(
                            row,
                            "status",
                            4
                        )
                })

            return result

        # =========================================================
        # COMPANY DETAIL
        # =========================================================

        if task == "company_detail":

            if not rows:
                return {}

            row = rows[0]

            return {
                "company_name":
                    EnterpriseFormatter._row_value(
                        row, "company_name", 0
                    ),
                "industry":
                    EnterpriseFormatter._row_value(
                        row, "industry", 1
                    ),
                "country":
                    EnterpriseFormatter._row_value(
                        row, "country", 2
                    ),
                "email":
                    EnterpriseFormatter._row_value(
                        row, "email", 3
                    ),
                "phone":
                    EnterpriseFormatter._row_value(
                        row, "phone", 4
                    ),
                "website":
                    EnterpriseFormatter._row_value(
                        row, "website", 5
                    ),
                "subscription_plan":
                    EnterpriseFormatter._row_value(
                        row, "subscription_plan", 6
                    ),
                "status":
                    EnterpriseFormatter._row_value(
                        row, "status", 7
                    ),
                "created_at":
                    EnterpriseFormatter._row_value(
                        row, "created_at", 8
                    )
            }

        # =========================================================
        # COMPANY SECURITY SUMMARY
        # =========================================================

        if task == "company_security_summary":

            if not rows:
                return {}

            row = rows[0]

            return {
                "company_name":
                    EnterpriseFormatter._row_value(
                        row,
                        "company_name",
                        0
                    ),
                "status":
                    EnterpriseFormatter._row_value(
                        row,
                        "status",
                        1
                    ),
                "user_count":
                    EnterpriseFormatter._row_value(
                        row,
                        "user_count",
                        2,
                        0
                    ),
                "threat_count":
                    EnterpriseFormatter._row_value(
                        row,
                        "threat_count",
                        3,
                        0
                    ),
                "alert_count":
                    EnterpriseFormatter._row_value(
                        row,
                        "alert_count",
                        4,
                        0
                    )
            }

        # =========================================================
        # USER LIST
        # =========================================================

        if task == "user_list":

            result = []

            for row in rows:

                result.append({
                    "name":
                        EnterpriseFormatter._row_value(
                            row,
                            "full_name",
                            0
                        ),
                    "email":
                        EnterpriseFormatter._row_value(
                            row,
                            "email",
                            1
                        ),
                    "role":
                        EnterpriseFormatter._row_value(
                            row,
                            "role",
                            2
                        ),
                    "status":
                        EnterpriseFormatter._row_value(
                            row,
                            "status",
                            3
                        ),
                    "last_login":
                        EnterpriseFormatter._row_value(
                            row,
                            "last_login",
                            4
                        )
                })

            return result

        # =========================================================
        # USER -> COMPANY
        # =========================================================

        if task == "user_company":

            result = []

            for row in rows:

                result.append({
                    "user_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "user_name",
                            0
                        ),
                    "email":
                        EnterpriseFormatter._row_value(
                            row,
                            "email",
                            1
                        ),
                    "role":
                        EnterpriseFormatter._row_value(
                            row,
                            "role",
                            2
                        ),
                    "user_status":
                        EnterpriseFormatter._row_value(
                            row,
                            "user_status",
                            3
                        ),
                    "last_login":
                        EnterpriseFormatter._row_value(
                            row,
                            "last_login",
                            4
                        ),
                    "company_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_name",
                            5
                        ),
                    "country":
                        EnterpriseFormatter._row_value(
                            row,
                            "country",
                            6
                        ),
                    "company_status":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_status",
                            7
                        )
                })

            return result

        # =========================================================
        # USER DETAIL
        # =========================================================

        if task == "user_detail":

            if not rows:
                return {}

            row = rows[0]

            return {
                "full_name":
                    EnterpriseFormatter._row_value(
                        row,
                        "full_name",
                        0
                    ),
                "email":
                    EnterpriseFormatter._row_value(
                        row,
                        "email",
                        1
                    ),
                "phone_number":
                    EnterpriseFormatter._row_value(
                        row,
                        "phone_number",
                        2
                    ),
                "role":
                    EnterpriseFormatter._row_value(
                        row,
                        "role",
                        3
                    ),
                "status":
                    EnterpriseFormatter._row_value(
                        row,
                        "status",
                        4
                    ),
                "last_login":
                    EnterpriseFormatter._row_value(
                        row,
                        "last_login",
                        5
                    ),
                "created_at":
                    EnterpriseFormatter._row_value(
                        row,
                        "created_at",
                        6
                    ),
                "company_name":
                    EnterpriseFormatter._row_value(
                        row,
                        "company_name",
                        7
                    ),
                "country":
                    EnterpriseFormatter._row_value(
                        row,
                        "country",
                        8
                    ),
                "company_status":
                    EnterpriseFormatter._row_value(
                        row,
                        "company_status",
                        9
                    )
            }

        # =========================================================
        # COMPANY USERS
        # =========================================================

        if task == "company_users":

            result = []

            for row in rows:

                result.append({
                    "name":
                        EnterpriseFormatter._row_value(
                            row,
                            "full_name",
                            0
                        ),
                    "email":
                        EnterpriseFormatter._row_value(
                            row,
                            "email",
                            1
                        ),
                    "role":
                        EnterpriseFormatter._row_value(
                            row,
                            "role",
                            2
                        ),
                    "status":
                        EnterpriseFormatter._row_value(
                            row,
                            "status",
                            3
                        ),
                    "last_login":
                        EnterpriseFormatter._row_value(
                            row,
                            "last_login",
                            4
                        )
                })

            return result

        # =========================================================
        # COMPANY USER COUNT
        # =========================================================

        if task in {
            "company_user_count",
            "top_company_by_users"
        }:

            result = []

            for row in rows:

                result.append({
                    "company_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_name",
                            0
                        ),
                    "user_count":
                        EnterpriseFormatter._row_value(
                            row,
                            "user_count",
                            1,
                            0
                        )
                })

            if task == "top_company_by_users":
                return result[0] if result else {}

            return result

        # =========================================================
        # THREATS
        # =========================================================

        if task in {
            "threat_list",
            "recent_threats",
            "company_threats"
        }:

            result = []

            for row in rows:

                result.append({
                    "title":
                        EnterpriseFormatter._row_value(
                            row,
                            "title",
                            0
                        ),
                    "severity":
                        EnterpriseFormatter._row_value(
                            row,
                            "severity",
                            1
                        ),
                    "status":
                        EnterpriseFormatter._row_value(
                            row,
                            "status",
                            2
                        ),
                    "description":
                        EnterpriseFormatter._row_value(
                            row,
                            "description",
                            3
                        ),
                    "detected_at":
                        EnterpriseFormatter._row_value(
                            row,
                            "detected_at",
                            4
                        ),
                    "company_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_name",
                            5
                        )
                })

            return result

        # =========================================================
        # ALERTS
        # =========================================================

        if task in {
            "alert_list",
            "company_alerts"
        }:

            result = []

            for row in rows:

                result.append({
                    "alert_type":
                        EnterpriseFormatter._row_value(
                            row,
                            "alert_type",
                            0
                        ),
                    "severity":
                        EnterpriseFormatter._row_value(
                            row,
                            "severity",
                            1
                        ),
                    "description":
                        EnterpriseFormatter._row_value(
                            row,
                            "description",
                            2
                        ),
                    "status":
                        EnterpriseFormatter._row_value(
                            row,
                            "status",
                            3
                        ),
                    "created_at":
                        EnterpriseFormatter._row_value(
                            row,
                            "created_at",
                            4
                        ),
                    "company_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_name",
                            5
                        )
                })

            return result

        # =========================================================
        # NETWORK SUMMARY
        # =========================================================

        if task == "network_summary":

            if not rows:

                return {
                    "flow_count": 0,
                    "total_packets": 0,
                    "total_bytes": 0,
                    "average_duration": 0
                }

            row = rows[0]

            return {
                "flow_count":
                    EnterpriseFormatter._row_value(
                        row,
                        "flow_count",
                        0,
                        0
                    ),
                "total_packets":
                    EnterpriseFormatter._row_value(
                        row,
                        "total_packets",
                        1,
                        0
                    ),
                "total_bytes":
                    EnterpriseFormatter._row_value(
                        row,
                        "total_bytes",
                        2,
                        0
                    ),
                "average_duration":
                    EnterpriseFormatter._row_value(
                        row,
                        "average_duration",
                        3,
                        0
                    )
            }

        # =========================================================
        # TOP IPS
        # =========================================================

        if task in {
            "top_source_ips",
            "top_destination_ips"
        }:

            result = []

            ip_key = (
                "source_ip"
                if task == "top_source_ips"
                else "destination_ip"
            )

            for row in rows:

                result.append({
                    "ip":
                        EnterpriseFormatter._row_value(
                            row,
                            ip_key,
                            0
                        ),
                    "flow_count":
                        EnterpriseFormatter._row_value(
                            row,
                            "flow_count",
                            1,
                            0
                        ),
                    "total_bytes":
                        EnterpriseFormatter._row_value(
                            row,
                            "total_bytes",
                            2,
                            0
                        )
                })

            return result

        # =========================================================
        # PROTOCOL STATISTICS
        # =========================================================

        if task == "protocol_statistics":

            result = []

            for row in rows:

                result.append({
                    "protocol":
                        EnterpriseFormatter._row_value(
                            row,
                            "protocol",
                            0
                        ),
                    "flow_count":
                        EnterpriseFormatter._row_value(
                            row,
                            "flow_count",
                            1,
                            0
                        ),
                    "total_packets":
                        EnterpriseFormatter._row_value(
                            row,
                            "total_packets",
                            2,
                            0
                        ),
                    "total_bytes":
                        EnterpriseFormatter._row_value(
                            row,
                            "total_bytes",
                            3,
                            0
                        )
                })

            return result

        # =========================================================
        # RECENT NETWORK FLOWS
        # =========================================================

        if task == "recent_network_flows":

            result = []

            for row in rows:

                result.append({
                    "source_ip":
                        EnterpriseFormatter._row_value(
                            row,
                            "source_ip",
                            0
                        ),
                    "destination_ip":
                        EnterpriseFormatter._row_value(
                            row,
                            "destination_ip",
                            1
                        ),
                    "protocol":
                        EnterpriseFormatter._row_value(
                            row,
                            "protocol",
                            2
                        ),
                    "packets":
                        EnterpriseFormatter._row_value(
                            row,
                            "packets",
                            3
                        ),
                    "bytes":
                        EnterpriseFormatter._row_value(
                            row,
                            "bytes",
                            4
                        ),
                    "duration":
                        EnterpriseFormatter._row_value(
                            row,
                            "duration",
                            5
                        ),
                    "detected_at":
                        EnterpriseFormatter._row_value(
                            row,
                            "detected_at",
                            6
                        )
                })

            return result

        # =========================================================
        # COMPANY NETWORK
        # =========================================================

        if task == "company_network_summary":

            if not rows:
                return {}

            row = rows[0]

            return {
                "company_name":
                    EnterpriseFormatter._row_value(
                        row,
                        "company_name",
                        0
                    ),
                "flow_count":
                    EnterpriseFormatter._row_value(
                        row,
                        "flow_count",
                        1,
                        0
                    ),
                "total_packets":
                    EnterpriseFormatter._row_value(
                        row,
                        "total_packets",
                        2,
                        0
                    ),
                "total_bytes":
                    EnterpriseFormatter._row_value(
                        row,
                        "total_bytes",
                        3,
                        0
                    )
            }

        # =========================================================
        # DASHBOARD / SECURITY / REPORT
        # =========================================================

        if task in {
            "dashboard_summary",
            "security_posture",
            "report"
        }:

            if not rows:
                return {}

            row = rows[0]

            if isinstance(row, dict):
                return dict(row)

            if task in {
                "security_posture",
                "report"
            }:

                return {
                    "organization_health": row[0],
                    "threat_level": row[1],
                    "ai_confidence": row[2],
                    "network_traffic": row[3],
                    "packets_per_second": row[4],
                    "latency": row[5],
                    "sensor_online": row[6],
                    "last_analysis": row[7]
                }

            return {
                "organization_health": row[0],
                "threat_level": row[1],
                "cpu_usage": row[2],
                "memory_usage": row[3],
                "disk_usage": row[4],
                "ai_confidence": row[5],
                "network_traffic": row[6],
                "packets_per_second": row[7],
                "latency": row[8],
                "sensor_online": row[9],
                "last_analysis": row[10]
            }

        # =========================================================
        # COMPANY SUBSCRIPTION
        # =========================================================

        if task == "company_subscription":

            if not rows:
                return {}

            row = rows[0]

            return {
                "company_name":
                    EnterpriseFormatter._row_value(
                        row,
                        "company_name",
                        0
                    ),
                "plan":
                    EnterpriseFormatter._row_value(
                        row,
                        "plan",
                        1
                    ),
                "billing_cycle":
                    EnterpriseFormatter._row_value(
                        row,
                        "billing_cycle",
                        2
                    ),
                "user_limit":
                    EnterpriseFormatter._row_value(
                        row,
                        "user_limit",
                        3
                    ),
                "current_users":
                    EnterpriseFormatter._row_value(
                        row,
                        "current_users",
                        4
                    ),
                "annual_price":
                    EnterpriseFormatter._row_value(
                        row,
                        "annual_price",
                        5
                    ),
                "renewal_date":
                    EnterpriseFormatter._row_value(
                        row,
                        "renewal_date",
                        6
                    ),
                "status":
                    EnterpriseFormatter._row_value(
                        row,
                        "status",
                        7
                    )
            }

        # =========================================================
        # SUBSCRIPTION SUMMARY
        # =========================================================

        if task == "subscription_summary":

            result = []

            for row in rows:

                result.append({
                    "company_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_name",
                            0
                        ),
                    "plan":
                        EnterpriseFormatter._row_value(
                            row,
                            "plan",
                            1
                        ),
                    "billing_cycle":
                        EnterpriseFormatter._row_value(
                            row,
                            "billing_cycle",
                            2
                        ),
                    "user_limit":
                        EnterpriseFormatter._row_value(
                            row,
                            "user_limit",
                            3
                        ),
                    "current_users":
                        EnterpriseFormatter._row_value(
                            row,
                            "current_users",
                            4
                        ),
                    "annual_price":
                        EnterpriseFormatter._row_value(
                            row,
                            "annual_price",
                            5
                        ),
                    "renewal_date":
                        EnterpriseFormatter._row_value(
                            row,
                            "renewal_date",
                            6
                        ),
                    "status":
                        EnterpriseFormatter._row_value(
                            row,
                            "status",
                            7
                        )
                })

            return result

        # =========================================================
        # OVER LIMIT
        # =========================================================

        if task == "over_limit_companies":

            result = []

            for row in rows:

                result.append({
                    "company_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_name",
                            0
                        ),
                    "plan":
                        EnterpriseFormatter._row_value(
                            row,
                            "plan",
                            1
                        ),
                    "user_limit":
                        EnterpriseFormatter._row_value(
                            row,
                            "user_limit",
                            2
                        ),
                    "current_users":
                        EnterpriseFormatter._row_value(
                            row,
                            "current_users",
                            3
                        ),
                    "extra_users":
                        EnterpriseFormatter._row_value(
                            row,
                            "extra_users",
                            4
                        ),
                    "annual_price":
                        EnterpriseFormatter._row_value(
                            row,
                            "annual_price",
                            5
                        ),
                    "renewal_date":
                        EnterpriseFormatter._row_value(
                            row,
                            "renewal_date",
                            6
                        )
                })

            return result

        # =========================================================
        # NOTIFICATIONS
        # =========================================================

        if task == "recent_notifications":

            result = []

            for row in rows:

                result.append({
                    "title":
                        EnterpriseFormatter._row_value(
                            row,
                            "title",
                            0
                        ),
                    "message":
                        EnterpriseFormatter._row_value(
                            row,
                            "message",
                            1
                        ),
                    "is_read":
                        EnterpriseFormatter._row_value(
                            row,
                            "is_read",
                            2
                        ),
                    "created_at":
                        EnterpriseFormatter._row_value(
                            row,
                            "created_at",
                            3
                        )
                })

            return result

        # =========================================================
        # AUDIT
        # =========================================================

        if task == "recent_audit_logs":

            result = []

            for row in rows:

                result.append({
                    "action":
                        EnterpriseFormatter._row_value(
                            row,
                            "action",
                            0
                        ),
                    "ip_address":
                        EnterpriseFormatter._row_value(
                            row,
                            "ip_address",
                            1
                        ),
                    "created_at":
                        EnterpriseFormatter._row_value(
                            row,
                            "created_at",
                            2
                        ),
                    "user_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "full_name",
                            3
                        ),
                    "company_name":
                        EnterpriseFormatter._row_value(
                            row,
                            "company_name",
                            4
                        )
                })

            return result

        # =========================================================
        # FALLBACK
        # =========================================================

        return [
            dict(row) if isinstance(row, dict) else row
            for row in rows
        ]