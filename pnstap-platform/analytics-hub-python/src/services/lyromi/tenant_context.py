from database import get_db_connection


class TenantContext:
    """Builds a compact, company-scoped context for LYROMI.

    This is intentionally separate from the older enterprise query registry so
    the AI layer cannot accidentally read another organization's records.
    """

    @staticmethod
    def build(company_id: int) -> dict:
        connection = get_db_connection()
        if connection is None:
            return {"available": False, "reason": "Database unavailable."}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT company_name, country, subscription_plan, status FROM companies WHERE id=%s", (company_id,))
                company = cursor.fetchone()
                if not company:
                    return {"available": False, "reason": "Workspace not found."}

                def count(sql, params=(company_id,)):
                    cursor.execute(sql, params)
                    row = cursor.fetchone()
                    return int(row["count"] or 0) if row else 0

                users = count("SELECT COUNT(*) AS count FROM users WHERE company_id=%s")
                active_users = count("SELECT COUNT(*) AS count FROM users WHERE company_id=%s AND status='Active'")
                alerts = count("SELECT COUNT(*) AS count FROM alerts WHERE company_id=%s")
                open_alerts = count("SELECT COUNT(*) AS count FROM alerts WHERE company_id=%s AND LOWER(status) IN ('open','active')")
                investigations = count("SELECT COUNT(*) AS count FROM investigations WHERE company_id=%s")
                open_investigations = count("SELECT COUNT(*) AS count FROM investigations WHERE company_id=%s AND LOWER(status) NOT IN ('closed','resolved')")
                assets = count("SELECT COUNT(*) AS count FROM asset_registry WHERE company_id=%s")
                identities = count("SELECT COUNT(*) AS count FROM identity_events WHERE company_id=%s")
                evidence = count("SELECT COUNT(*) AS count FROM evidence WHERE company_id=%s")
                timeline = count("SELECT COUNT(*) AS count FROM security_timeline WHERE company_id=%s")
                drift = count("SELECT COUNT(*) AS count FROM drift_events WHERE company_id=%s")
                telemetry = count("SELECT COUNT(*) AS count FROM sensor_telemetry WHERE company_id=%s")
                sensors = count("SELECT COUNT(*) AS count FROM sensor_enrollments WHERE company_id=%s")
                integrations = count("SELECT COUNT(*) AS count FROM security_integrations WHERE company_id=%s")

                cursor.execute("SELECT severity, COUNT(*) AS count FROM alerts WHERE company_id=%s GROUP BY severity ORDER BY severity", (company_id,))
                alert_breakdown = {str(row["severity"]): int(row["count"]) for row in cursor.fetchall()}

                cursor.execute("SELECT event_type, severity, message, occurred_at FROM security_timeline WHERE company_id=%s ORDER BY occurred_at DESC LIMIT 8", (company_id,))
                recent_timeline = cursor.fetchall()

                cursor.execute("SELECT subject_type, subject_key, change_type, severity, detected_at FROM drift_events WHERE company_id=%s ORDER BY detected_at DESC LIMIT 8", (company_id,))
                recent_drift = cursor.fetchall()

                cursor.execute("SELECT title, status, priority, summary, updated_at FROM investigations WHERE company_id=%s ORDER BY updated_at DESC LIMIT 8", (company_id,))
                recent_investigations = cursor.fetchall()

                return {
                    "available": True,
                    "workspace": company,
                    "counts": {"users": users, "active_users": active_users, "alerts": alerts, "open_alerts": open_alerts, "investigations": investigations, "open_investigations": open_investigations, "assets": assets, "identity_events": identities, "evidence": evidence, "timeline_events": timeline, "drift_events": drift, "sensor_telemetry": telemetry, "sensors": sensors, "integrations": integrations},
                    "alert_breakdown": alert_breakdown,
                    "recent_timeline": recent_timeline,
                    "recent_drift": recent_drift,
                    "recent_investigations": recent_investigations,
                }
        finally:
            connection.close()
