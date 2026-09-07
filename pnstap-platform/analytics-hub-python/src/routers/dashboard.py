from fastapi import APIRouter, Depends, HTTPException
from database import get_db_connection
from auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def _rows(cursor, query, params):
    cursor.execute(query, params)
    return cursor.fetchall()


@router.get("/")
def get_dashboard(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    company_id = current_user["company_id"]

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE company_id = %s", (company_id,))
        users = cursor.fetchone()["total"]

        alerts = _rows(
            cursor,
            """
            SELECT id, company_id, alert_type, severity, description, status, created_at
            FROM alerts
            WHERE company_id = %s
            ORDER BY created_at DESC
            LIMIT 50
            """,
            (company_id,),
        )

        network_flows = _rows(
            cursor,
            """
            SELECT id, company_id, source_ip, destination_ip, protocol, packets, bytes, duration, detected_at
            FROM network_flows
            WHERE company_id = %s
            ORDER BY detected_at DESC
            LIMIT 50
            """,
            (company_id,),
        )

        notifications = _rows(
            cursor,
            """
            SELECT id, company_id, title, message, is_read, created_at
            FROM notifications
            WHERE company_id = %s
            ORDER BY created_at DESC
            LIMIT 50
            """,
            (company_id,),
        )

        sensors = _rows(
            cursor,
            """
            SELECT id, company_id, sensor_name, environment_name, environment_type,
                   status, registered_at, last_heartbeat, last_status_change,
                   created_at, updated_at
            FROM sensor_enrollments
            WHERE company_id = %s
            ORDER BY updated_at DESC
            """,
            (company_id,),
        )

        active_alerts = [a for a in alerts if str(a.get("status") or "").lower() not in {"resolved", "closed", "dismissed"}]
        online_sensors = [s for s in sensors if str(s.get("status") or "").upper() in {"ONLINE", "ACTIVE", "CONNECTED", "HEALTHY"}]

        activity = []
        for alert in alerts:
            activity.append({
                "id": f"alert-{alert['id']}",
                "title": alert.get("alert_type") or "Security alert",
                "description": alert.get("description"),
                "severity": alert.get("severity") or "info",
                "status": alert.get("status") or "open",
                "location": "Security Network",
                "timestamp": str(alert.get("created_at")) if alert.get("created_at") else "Recent",
            })
        for note in notifications:
            activity.append({
                "id": f"notification-{note['id']}",
                "title": note.get("title") or "Security notification",
                "description": note.get("message"),
                "severity": "info",
                "status": "read" if note.get("is_read") else "unread",
                "location": "Cypheris",
                "timestamp": str(note.get("created_at")) if note.get("created_at") else "Recent",
            })
        for flow in network_flows:
            activity.append({
                "id": f"flow-{flow['id']}",
                "title": f"{flow.get('protocol') or 'NETWORK'} network flow",
                "description": f"{flow.get('source_ip') or 'Unknown'} → {flow.get('destination_ip') or 'Unknown'}",
                "severity": "info",
                "status": "observed",
                "location": "PNSTAP",
                "timestamp": str(flow.get("detected_at")) if flow.get("detected_at") else "Recent",
            })

        activity.sort(key=lambda item: item.get("timestamp", ""), reverse=True)

        threat_level = "CRITICAL" if any(str(a.get("severity") or "").upper() == "CRITICAL" for a in active_alerts) else "HIGH" if any(str(a.get("severity") or "").upper() == "HIGH" for a in active_alerts) else "LOW"
        security_score = max(0, 100 - min(len(active_alerts) * 10, 100))

        return {
            "status": "success",
            "organization": current_user.get("company_id"),
            "users": users,
            "active_users": users,
            "threats": len(active_alerts),
            "incidents": len(active_alerts),
            "events": len(activity),
            "security_score": security_score,
            "health": security_score,
            "threat_level": threat_level,
            "network_traffic": sum(int(flow.get("bytes") or 0) for flow in network_flows),
            "packets_per_second": sum(int(flow.get("packets") or 0) for flow in network_flows),
            "latency": 0,
            "sensor_online": bool(online_sensors),
            "ai_confidence": 0,
            "last_analysis": str(activity[0]["timestamp"]) if activity else None,
            "activity": activity[:100],
            "signals": [],
            "threat_feed": alerts[:20],
            "resources": {"CPU": 0, "Memory": 0, "Disk": 0},
            "integrations": {"sensors": len(online_sensors), "clouds": 0, "apis": 0},
            "organizations": 1,
            "telemetry": {"network_flows": len(network_flows), "notifications": len(notifications), "sensors": len(sensors)},
            "lyromi_message": (
                "No active security alerts were found. Continue routine monitoring."
                if not active_alerts else
                f"{len(active_alerts)} active security alert(s) require review in the Threat Center."
            ),
        }
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to load dashboard telemetry.") from error
    finally:
        connection.close()
