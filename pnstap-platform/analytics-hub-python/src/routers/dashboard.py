from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
async def get_dashboard():

    conn = get_db_connection()

    if conn is None:
        return {
            "status": "error",
            "message": "Database connection failed."
        }

    try:

        cur = conn.cursor()

        # ============================================================
        # ORGANIZATIONS
        # ============================================================

        cur.execute("""
            SELECT COUNT(*) AS total
            FROM companies;
        """)

        organizations = cur.fetchone()["total"]


        # ============================================================
        # USERS
        # ============================================================

        cur.execute("""
            SELECT COUNT(*) AS total
            FROM users;
        """)

        users = cur.fetchone()["total"]


        # ============================================================
        # DASHBOARD METRICS
        # ============================================================

        cur.execute("""
            SELECT
                organization_health,
                threat_level,
                network_traffic,
                packets_per_second,
                latency,
                sensor_online,
                ai_confidence,
                last_analysis,
                cpu_usage,
                memory_usage,
                disk_usage
            FROM dashboard_metrics
            ORDER BY id DESC
            LIMIT 1;
        """)

        metrics = cur.fetchone()

        if metrics is None:

            metrics = {
                "organization_health": 0,
                "threat_level": "LOW",
                "network_traffic": 0,
                "packets_per_second": 0,
                "latency": 0,
                "sensor_online": False,
                "ai_confidence": 0,
                "last_analysis": None,
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
            }


        # ============================================================
        # THREATS
        # ============================================================

        cur.execute("""
            SELECT
                id,
                company_id,
                title,
                severity,
                status,
                detected_at
            FROM threats
            ORDER BY detected_at DESC
            LIMIT 20;
        """)

        threats = cur.fetchall()


        # ============================================================
        # ACTIVE THREATS
        # ============================================================

        active_threats = 0

        for threat in threats:

            status = str(
                threat.get("status") or ""
            ).lower()

            if status not in (
                "resolved",
                "closed",
                "dismissed"
            ):
                active_threats += 1


        # ============================================================
        # PNSTAP NETWORK FLOWS
        # ============================================================

        cur.execute("""
            SELECT
                id,
                company_id,
                source_ip,
                destination_ip,
                protocol,
                packets,
                bytes,
                duration,
                detected_at
            FROM network_flows
            ORDER BY detected_at DESC
            LIMIT 50;
        """)

        network_flows = cur.fetchall()


        # ============================================================
        # PNSTAP ACTIVITY LOGS
        # ============================================================

        cur.execute("""
            SELECT
                id,
                company_id,
                activity,
                created_at
            FROM activity_logs
            ORDER BY created_at DESC
            LIMIT 50;
        """)

        activity_logs = cur.fetchall()


        # ============================================================
        # SENSOR ENROLLMENTS
        # ============================================================

        cur.execute("""
            SELECT
                id,
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                status,
                last_heartbeat
            FROM sensor_enrollments
            ORDER BY updated_at DESC;
        """)

        sensors = cur.fetchall()


        # ============================================================
        # SENSOR COUNT
        # ============================================================

        sensor_count = 0

        for sensor in sensors:

            status = str(
                sensor.get("status") or ""
            ).upper()

            if status in (
                "ONLINE",
                "ACTIVE",
                "CONNECTED",
                "HEALTHY"
            ):
                sensor_count += 1


        # ============================================================
        # ACTIVITY
        # ============================================================

        activity = []


        # ------------------------------------------------------------
        # Threat activity
        # ------------------------------------------------------------

        for threat in threats:

            activity.append({
                "id": f"threat-{threat['id']}",

                "title": threat.get(
                    "title",
                    "Security threat"
                ),

                "severity": threat.get(
                    "severity",
                    "info"
                ),

                "status": threat.get(
                    "status",
                    "unknown"
                ),

                "location": "Security Network",

                "timestamp": str(
                    threat.get(
                        "detected_at"
                    )
                )
                if threat.get("detected_at")
                else "Recent"
            })


        # ------------------------------------------------------------
        # PNSTAP activity logs
        # ------------------------------------------------------------

        for log in activity_logs:

            activity.append({
                "id": f"log-{log['id']}",

                "title": log.get(
                    "activity",
                    "PNSTAP activity"
                ),

                "severity": "info",

                "status": "logged",

                "location": "PNSTAP",

                "timestamp": str(
                    log.get(
                        "created_at"
                    )
                )
                if log.get("created_at")
                else "Recent"
            })


        # ------------------------------------------------------------
        # Network flow activity
        # ------------------------------------------------------------

        for flow in network_flows:

            activity.append({
                "id": f"flow-{flow['id']}",

                "title": (
                    f"{flow.get('protocol', 'NETWORK')} "
                    "network flow"
                ),

                "severity": "info",

                "status": "observed",

                "location": (
                    f"{flow.get('source_ip', 'Unknown')} → "
                    f"{flow.get('destination_ip', 'Unknown')}"
                ),

                "timestamp": str(
                    flow.get(
                        "detected_at"
                    )
                )
                if flow.get("detected_at")
                else "Recent"
            })


        # ============================================================
        # SORT ACTIVITY
        # ============================================================

        activity = sorted(
            activity,
            key=lambda item: item.get(
                "timestamp",
                ""
            ),
            reverse=True
        )


        # ============================================================
        # CESIUM SIGNALS
        #
        # We intentionally do not manufacture coordinates.
        # Geographic enrichment will be added later.
        # ============================================================

        signals = []


        # ============================================================
        # THREAT FEED
        # ============================================================

        threat_feed = []

        for threat in threats:

            threat_feed.append({
                "id": threat.get("id"),

                "title": threat.get(
                    "title",
                    "Threat intelligence update"
                ),

                "severity": threat.get(
                    "severity",
                    "info"
                ),

                "status": threat.get(
                    "status",
                    "unknown"
                ),

                "timestamp": str(
                    threat.get(
                        "detected_at"
                    )
                )
                if threat.get("detected_at")
                else "Recent"
            })


        # ============================================================
        # SECURITY SCORE
        # ============================================================

        security_score = float(
            metrics.get(
                "organization_health",
                0
            ) or 0
        )


        # ============================================================
        # SYSTEM RESOURCES
        # ============================================================

        resources = {

            "CPU": float(
                metrics.get(
                    "cpu_usage",
                    0
                ) or 0
            ),

            "Memory": float(
                metrics.get(
                    "memory_usage",
                    0
                ) or 0
            ),

            "Disk": float(
                metrics.get(
                    "disk_usage",
                    0
                ) or 0
            )
        }


        # ============================================================
        # EXECUTIVE SUMMARY
        # ============================================================

        executive_summary = f"""
Executive Security Summary

• Organization Health: {metrics["organization_health"]}%
• Threat Level: {metrics["threat_level"]}
• Active Threats: {active_threats}
• Network Flows: {len(network_flows)}
• Activity Events: {len(activity_logs)}
• Sensors Online: {sensor_count}
• CPU Usage: {metrics["cpu_usage"]}%
• Memory Usage: {metrics["memory_usage"]}%
• Disk Usage: {metrics["disk_usage"]}%
• AI Confidence: {float(metrics["ai_confidence"])}%

Recommendation:
"""

        if active_threats == 0:

            executive_summary += (
                "No active threats detected. "
                "Continue routine monitoring."
            )

        else:

            executive_summary += (
                f"There are {active_threats} active threat(s). "
                "Review the Threat Center for investigation."
            )


        # ============================================================
        # RESPONSE
        # ============================================================

        return {

            "status": "success",

            "organization": "Cypheris Technologies",

            # --------------------------------------------------------
            # KPI
            # --------------------------------------------------------

            "users": users,

            "active_users": users,

            "threats": active_threats,

            "incidents": 0,

            "events": len(activity),

            "security_score": security_score,

            # --------------------------------------------------------
            # METRICS
            # --------------------------------------------------------

            "health": metrics["organization_health"],

            "threat_level": metrics["threat_level"],

            "network_traffic": metrics["network_traffic"],

            "packets_per_second": metrics["packets_per_second"],

            "latency": metrics["latency"],

            "sensor_online": metrics["sensor_online"],

            "ai_confidence": float(
                metrics["ai_confidence"]
            ),

            "last_analysis": str(
                metrics["last_analysis"]
            ),

            # --------------------------------------------------------
            # DATA
            # --------------------------------------------------------

            "activity": activity,

            "signals": signals,

            "threat_feed": threat_feed,

            "resources": resources,

            # --------------------------------------------------------
            # INTEGRATIONS
            # --------------------------------------------------------

            "integrations": {
                "sensors": sensor_count,
                "clouds": 0,
                "apis": 0
            },

            # --------------------------------------------------------
            # COUNTS
            # --------------------------------------------------------

            "organizations": organizations,

            # --------------------------------------------------------
            # PNSTAP TELEMETRY STATUS
            # --------------------------------------------------------

            "telemetry": {
                "network_flows": len(
                    network_flows
                ),

                "activity_logs": len(
                    activity_logs
                ),

                "sensors": len(
                    sensors
                )
            },

            # --------------------------------------------------------
            # LYROMI
            # --------------------------------------------------------

            "lyromi_message": executive_summary
        }


    except Exception as error:

        print(
            "Dashboard query failed:",
            error
        )

        return {
            "status": "error",
            "message": str(error)
        }

    finally:

        conn.close()