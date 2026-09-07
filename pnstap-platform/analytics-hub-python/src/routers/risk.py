from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from database import get_db_connection

router = APIRouter(prefix="/api/risk", tags=["risk"])


def _severity_score(value):
    return {"CRITICAL": 100, "HIGH": 75, "MEDIUM": 50, "LOW": 25, "INFO": 10}.get(str(value or "INFO").upper(), 10)


@router.get("/context")
def context_graph(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    company_id = current_user["company_id"]
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, sensor_name, environment_name, environment_type, status,
                       last_heartbeat, created_at
                FROM sensor_enrollments
                WHERE company_id = %s
                ORDER BY updated_at DESC
                LIMIT 100
                """,
                (company_id,),
            )
            sensors = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, connection_name, environment_name, environment_type,
                       integration_type, provider, api_platform, status,
                       last_heartbeat, created_at
                FROM security_integrations
                WHERE company_id = %s
                ORDER BY updated_at DESC
                LIMIT 100
                """,
                (company_id,),
            )
            integrations = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, severity, alert_type, status, created_at
                FROM alerts
                WHERE company_id = %s
                ORDER BY created_at DESC
                LIMIT 100
                """,
                (company_id,),
            )
            alerts = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, source_ip::text AS source_ip, destination_ip::text AS destination_ip,
                       protocol, packets, bytes, detected_at
                FROM network_flows
                WHERE company_id = %s
                ORDER BY detected_at DESC
                LIMIT 200
                """,
                (company_id,),
            )
            flows = cursor.fetchall()

            cursor.execute(
                "SELECT id, full_name, role, status FROM users WHERE company_id = %s ORDER BY id LIMIT 100",
                (company_id,),
            )
            users = cursor.fetchall()

        nodes = []
        edges = []
        seen = set()

        def add_node(node_id, node_type, label, status=None, metadata=None, risk=0):
            if node_id in seen:
                return
            seen.add(node_id)
            nodes.append({
                "id": node_id,
                "type": node_type,
                "label": label,
                "status": status,
                "risk": risk,
                "metadata": metadata or {},
            })

        add_node("company", "organization", "Company", "active", {"company_id": company_id})

        for item in sensors:
            nid = f"sensor:{item['id']}"
            add_node(nid, "environment", item["environment_name"], item["status"], {
                "source": item["sensor_name"], "environment_type": item["environment_type"]
            })
            edges.append({"source": "company", "target": nid, "relation": "monitors"})

        for item in integrations:
            nid = f"integration:{item['id']}"
            add_node(nid, "integration", item["connection_name"], item["status"], {
                "provider": item["provider"], "api_platform": item["api_platform"],
                "environment": item["environment_name"], "environment_type": item["environment_type"]
            })
            edges.append({"source": "company", "target": nid, "relation": "connects"})

        for item in users:
            nid = f"identity:{item['id']}"
            add_node(nid, "identity", item["full_name"], item["status"], {"role": item["role"]})
            edges.append({"source": "company", "target": nid, "relation": "identity"})

        for item in alerts:
            nid = f"alert:{item['id']}"
            score = _severity_score(item["severity"])
            add_node(nid, "finding", item["alert_type"], item["status"], {
                "severity": item["severity"], "created_at": item["created_at"].isoformat() if item["created_at"] else None
            }, score)
            edges.append({"source": "company", "target": nid, "relation": "detected"})

        for item in flows:
            source = item["source_ip"]
            destination = item["destination_ip"]
            if source:
                sid = f"network:{source}"
                add_node(sid, "network", source, "observed", {"ip": source})
            if destination:
                did = f"network:{destination}"
                add_node(did, "network", destination, "observed", {"ip": destination})
            if source and destination:
                edges.append({
                    "source": f"network:{source}",
                    "target": f"network:{destination}",
                    "relation": "network_flow",
                    "protocol": item["protocol"],
                    "bytes": item["bytes"],
                })

        risk_score = 0
        if alerts:
            risk_score = round(sum(_severity_score(a["severity"]) for a in alerts) / len(alerts))
        exposure_count = sum(1 for f in flows if f["source_ip"] and f["destination_ip"])

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "nodes": len(nodes),
                "relationships": len(edges),
                "alerts": len(alerts),
                "network_observations": len(flows),
                "connected_sources": len(sensors) + len(integrations),
                "average_alert_risk": risk_score,
                "network_relationships": exposure_count,
            },
            "evidence": {
                "sensors": len(sensors),
                "integrations": len(integrations),
                "identities": len(users),
                "findings": len(alerts),
                "network_flows": len(flows),
            },
        }
    finally:
        connection.close()


@router.get("/attack-paths")
def attack_paths(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, severity, alert_type, description, status, created_at
                FROM alerts
                WHERE company_id = %s AND LOWER(status) NOT IN ('closed', 'resolved')
                ORDER BY created_at DESC
                LIMIT 100
                """,
                (current_user["company_id"],),
            )
            alerts = cursor.fetchall()

            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM network_flows
                WHERE company_id = %s
                """,
                (current_user["company_id"],),
            )
            flow_count = cursor.fetchone()["count"]

        paths = []
        # A path is only surfaced when there is supporting telemetry plus an open finding.
        if flow_count and alerts:
            for alert in alerts:
                score = _severity_score(alert["severity"])
                if score < 50:
                    continue
                paths.append({
                    "id": f"alert-path:{alert['id']}",
                    "title": alert["alert_type"],
                    "severity": alert["severity"],
                    "status": alert["status"],
                    "score": score + min(int(flow_count), 25),
                    "evidence": ["open finding", "network telemetry"],
                    "description": alert["description"] or "Connected telemetry supports further investigation of this finding.",
                })

        paths.sort(key=lambda p: p["score"], reverse=True)
        return {
            "paths": paths[:20],
            "calculated": bool(paths),
            "reason": None if paths else "Not enough connected evidence to calculate a defensible attack path.",
        }
    finally:
        connection.close()
