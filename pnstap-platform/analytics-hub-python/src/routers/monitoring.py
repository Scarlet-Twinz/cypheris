from collections import Counter

from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from database import get_db_connection

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


def _conn_or_503():
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    return connection


@router.get("/alerts")
def alerts(current_user: dict = Depends(get_current_user)):
    connection = _conn_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, severity, alert_type, description, status, created_at
                FROM alerts
                WHERE company_id = %s
                ORDER BY CASE UPPER(severity)
                    WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3 WHEN 'LOW' THEN 4 ELSE 5 END,
                    created_at DESC
                LIMIT 200
                """,
                (current_user["company_id"],),
            )
            rows = cursor.fetchall()
        counts = Counter(str(row["severity"] or "INFO").upper() for row in rows)
        open_count = sum(1 for row in rows if str(row["status"] or "").lower() not in {"closed", "resolved"})
        return {
            "alerts": rows,
            "summary": {
                "total": len(rows),
                "open": open_count,
                "critical": counts.get("CRITICAL", 0),
                "high": counts.get("HIGH", 0),
                "medium": counts.get("MEDIUM", 0),
                "low": counts.get("LOW", 0),
            },
        }
    finally:
        connection.close()


@router.get("/network")
def network(current_user: dict = Depends(get_current_user)):
    connection = _conn_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT source_ip::text AS source_ip, destination_ip::text AS destination_ip,
                       protocol, packets, bytes, duration, detected_at
                FROM network_flows
                WHERE company_id = %s
                ORDER BY detected_at DESC
                LIMIT 500
                """,
                (current_user["company_id"],),
            )
            rows = cursor.fetchall()
        protocols = Counter(str(row["protocol"] or "UNKNOWN").upper() for row in rows)
        sources = Counter(row["source_ip"] for row in rows if row["source_ip"])
        destinations = Counter(row["destination_ip"] for row in rows if row["destination_ip"])
        return {
            "flows": rows,
            "summary": {
                "flows": len(rows),
                "unique_sources": len(sources),
                "unique_destinations": len(destinations),
                "bytes": sum(int(row["bytes"] or 0) for row in rows),
                "packets": sum(int(row["packets"] or 0) for row in rows),
                "protocols": dict(protocols),
                "top_sources": [{"address": k, "observations": v} for k, v in sources.most_common(8)],
                "top_destinations": [{"address": k, "observations": v} for k, v in destinations.most_common(8)],
            },
        }
    finally:
        connection.close()


@router.get("/assets")
def assets(current_user: dict = Depends(get_current_user)):
    connection = _conn_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, sensor_name AS name, environment_name, environment_type,
                       status, last_heartbeat, created_at, 'sensor' AS source
                FROM sensor_enrollments
                WHERE company_id = %s
                ORDER BY updated_at DESC
                LIMIT 100
                """,
                (current_user["company_id"],),
            )
            sensors = cursor.fetchall()
            cursor.execute(
                """
                SELECT id, connection_name AS name, environment_name, environment_type,
                       status, last_heartbeat, created_at, 'integration' AS source
                FROM security_integrations
                WHERE company_id = %s
                ORDER BY updated_at DESC
                LIMIT 100
                """,
                (current_user["company_id"],),
            )
            integrations = cursor.fetchall()
        assets = sensors + integrations
        assets.sort(key=lambda row: row["created_at"] or 0, reverse=True)
        return {
            "assets": assets[:200],
            "summary": {
                "total": len(assets),
                "sensors": len(sensors),
                "integrations": len(integrations),
                "active": sum(1 for item in assets if str(item["status"] or "").lower() in {"active", "online", "registered"}),
            },
        }
    finally:
        connection.close()


@router.get("/notifications")
def notifications(current_user: dict = Depends(get_current_user)):
    connection = _conn_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, message, is_read, created_at
                FROM notifications
                WHERE company_id = %s
                ORDER BY created_at DESC
                LIMIT 100
                """,
                (current_user["company_id"],),
            )
            rows = cursor.fetchall()
        return {"notifications": rows, "unread": sum(1 for row in rows if not row["is_read"])}
    finally:
        connection.close()
