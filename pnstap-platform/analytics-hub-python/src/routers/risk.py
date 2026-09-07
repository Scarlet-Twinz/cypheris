from collections import Counter

from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from database import get_db_connection

router = APIRouter(prefix="/api/risk", tags=["risk"])


SEVERITY_SCORE = {"CRITICAL": 100, "HIGH": 75, "MEDIUM": 50, "LOW": 25, "INFO": 10}


def _severity_score(value):
    return SEVERITY_SCORE.get(str(value or "INFO").upper(), 10)


def _risk_band(score):
    if score >= 90:
        return "CRITICAL"
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _row_time(value):
    return value.isoformat() if value else None


def _recommendation(severity, flow_count):
    level = str(severity or "INFO").upper()
    if level == "CRITICAL":
        action = "Investigate immediately, validate affected assets, and contain the highest-risk relationship."
    elif level == "HIGH":
        action = "Investigate the affected relationship, validate exposure, and apply the appropriate control or remediation."
    elif level == "MEDIUM":
        action = "Validate the finding against connected telemetry and schedule remediation based on confirmed exposure."
    else:
        action = "Review the finding and collect enough telemetry to determine whether remediation is required."
    if flow_count:
        action += " Network telemetry is available for correlation."
    return action


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
                FROM sensor_enrollments WHERE company_id = %s
                ORDER BY updated_at DESC LIMIT 100
                """, (company_id,),
            )
            sensors = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, connection_name, environment_name, environment_type,
                       integration_type, provider, api_platform, status,
                       last_heartbeat, created_at
                FROM security_integrations WHERE company_id = %s
                ORDER BY updated_at DESC LIMIT 100
                """, (company_id,),
            )
            integrations = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, severity, alert_type, status, created_at
                FROM alerts WHERE company_id = %s
                ORDER BY created_at DESC LIMIT 100
                """, (company_id,),
            )
            alerts = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, source_ip::text AS source_ip, destination_ip::text AS destination_ip,
                       protocol, packets, bytes, detected_at
                FROM network_flows WHERE company_id = %s
                ORDER BY detected_at DESC LIMIT 200
                """, (company_id,),
            )
            flows = cursor.fetchall()

            cursor.execute(
                "SELECT id, full_name, role, status FROM users WHERE company_id = %s ORDER BY id LIMIT 100",
                (company_id,),
            )
            users = cursor.fetchall()

        nodes, edges, seen = [], [], set()

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
                "source": item["sensor_name"], "environment_type": item["environment_type"],
                "last_heartbeat": _row_time(item["last_heartbeat"]),
            })
            edges.append({"source": "company", "target": nid, "relation": "monitors"})

        for item in integrations:
            nid = f"integration:{item['id']}"
            add_node(nid, "integration", item["connection_name"], item["status"], {
                "provider": item["provider"], "api_platform": item["api_platform"],
                "environment": item["environment_name"], "environment_type": item["environment_type"],
                "last_heartbeat": _row_time(item["last_heartbeat"]),
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
                "severity": item["severity"], "created_at": _row_time(item["created_at"]),
            }, score)
            edges.append({"source": "company", "target": nid, "relation": "detected"})

        for item in flows:
            source, destination = item["source_ip"], item["destination_ip"]
            if source:
                add_node(f"network:{source}", "network", source, "observed", {"ip": source})
            if destination:
                add_node(f"network:{destination}", "network", destination, "observed", {"ip": destination})
            if source and destination:
                edges.append({
                    "source": f"network:{source}", "target": f"network:{destination}",
                    "relation": "network_flow", "protocol": item["protocol"], "bytes": item["bytes"],
                })

        average_alert_risk = round(sum(_severity_score(a["severity"]) for a in alerts) / len(alerts)) if alerts else 0
        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "nodes": len(nodes), "relationships": len(edges), "alerts": len(alerts),
                "network_observations": len(flows), "connected_sources": len(sensors) + len(integrations),
                "average_alert_risk": average_alert_risk,
                "network_relationships": sum(1 for e in edges if e["relation"] == "network_flow"),
            },
            "evidence": {
                "sensors": len(sensors), "integrations": len(integrations),
                "identities": len(users), "findings": len(alerts), "network_flows": len(flows),
            },
        }
    finally:
        connection.close()


@router.get("/attack-paths")
def attack_paths(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    company_id = current_user["company_id"]
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, severity, alert_type, description, status, created_at
                FROM alerts WHERE company_id = %s
                  AND LOWER(status) NOT IN ('closed', 'resolved')
                ORDER BY created_at DESC LIMIT 100
                """, (company_id,),
            )
            alerts = cursor.fetchall()

            cursor.execute(
                """
                SELECT source_ip::text AS source_ip, destination_ip::text AS destination_ip,
                       protocol, bytes, detected_at
                FROM network_flows WHERE company_id = %s
                ORDER BY detected_at DESC LIMIT 500
                """, (company_id,),
            )
            flows = cursor.fetchall()

        if not alerts or not flows:
            return {
                "paths": [], "calculated": False,
                "reason": "Not enough connected evidence to calculate a defensible attack path.",
                "evidence": {"open_findings": len(alerts), "network_flows": len(flows)},
            }

        source_counts = Counter(f["source_ip"] for f in flows if f["source_ip"])
        destination_counts = Counter(f["destination_ip"] for f in flows if f["destination_ip"])
        total_bytes = sum(int(f["bytes"] or 0) for f in flows)
        paths = []

        for alert in alerts:
            base = _severity_score(alert["severity"])
            exposure_bonus = min(15, len(source_counts) * 2)
            reachability_bonus = min(10, len(destination_counts))
            telemetry_bonus = 10 if total_bytes > 0 else 0
            score = min(100, base + exposure_bonus + reachability_bonus + telemetry_bonus)
            source = source_counts.most_common(1)[0][0] if source_counts else "Observed network"
            target = destination_counts.most_common(1)[0][0] if destination_counts else "Protected environment"
            paths.append({
                "id": f"path:{alert['id']}",
                "title": alert["alert_type"],
                "severity": alert["severity"],
                "band": _risk_band(score),
                "status": alert["status"],
                "score": score,
                "hops": 2 if source != target else 1,
                "entry": source,
                "target": target,
                "evidence": ["open finding", "network telemetry"],
                "description": alert["description"] or "Connected telemetry supports further investigation of this finding.",
                "created_at": _row_time(alert["created_at"]),
            })

        paths.sort(key=lambda p: (p["score"], p["created_at"] or ""), reverse=True)
        return {
            "paths": paths[:20], "calculated": bool(paths),
            "reason": None,
            "evidence": {"open_findings": len(alerts), "network_flows": len(flows)},
        }
    finally:
        connection.close()


@router.get("/priorities")
def priorities(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    company_id = current_user["company_id"]
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, severity, alert_type, description, status, created_at
                FROM alerts WHERE company_id = %s
                  AND LOWER(status) NOT IN ('closed', 'resolved')
                ORDER BY created_at DESC LIMIT 100
                """, (company_id,),
            )
            alerts = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS count FROM network_flows WHERE company_id = %s", (company_id,)
            )
            flow_count = cursor.fetchone()["count"]

        items = []
        for alert in alerts:
            base = _severity_score(alert["severity"])
            telemetry_bonus = min(20, int(flow_count))
            score = min(100, base + telemetry_bonus)
            items.append({
                "id": alert["id"],
                "title": alert["alert_type"],
                "description": alert["description"] or "No additional finding description was recorded.",
                "score": score,
                "band": _risk_band(score),
                "severity": alert["severity"],
                "status": alert["status"],
                "created_at": _row_time(alert["created_at"]),
                "evidence": ["open finding"] + (["network telemetry"] if flow_count else []),
                "recommendation": _recommendation(alert["severity"], flow_count),
            })
        items.sort(key=lambda item: (item["score"], item["created_at"] or ""), reverse=True)
        return {"items": items[:20], "total_open_findings": len(alerts), "telemetry": int(flow_count)}
    finally:
        connection.close()


@router.get("/choke-points")
def choke_points(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    company_id = current_user["company_id"]
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT source_ip::text AS source_ip, destination_ip::text AS destination_ip,
                       protocol, bytes, detected_at
                FROM network_flows WHERE company_id = %s
                ORDER BY detected_at DESC LIMIT 1000
                """, (company_id,),
            )
            flows = cursor.fetchall()
            cursor.execute(
                """
                SELECT severity, status FROM alerts WHERE company_id = %s
                  AND LOWER(status) NOT IN ('closed', 'resolved')
                """, (company_id,),
            )
            alerts = cursor.fetchall()

        if not flows:
            return {
                "items": [], "calculated": False,
                "reason": "No network telemetry is available to identify repeated relationship choke points.",
                "evidence": {"network_flows": 0, "open_findings": len(alerts)},
            }

        node_degree = Counter()
        pair_counts = Counter()
        for flow in flows:
            source = flow["source_ip"]
            destination = flow["destination_ip"]
            if source:
                node_degree[source] += 1
            if destination:
                node_degree[destination] += 1
            if source and destination:
                pair_counts[(source, destination)] += 1

        highest_severity = max((_severity_score(a["severity"]) for a in alerts), default=0)
        items = []
        for node, degree in node_degree.most_common(10):
            score = min(100, degree * 5 + min(25, highest_severity // 4))
            items.append({
                "node": node,
                "score": score,
                "band": _risk_band(score),
                "observations": degree,
                "related_paths": sum(count for (source, destination), count in pair_counts.items() if source == node or destination == node),
                "reason": "Repeated network relationships make this entity a useful investigation and control point.",
            })

        return {
            "items": items,
            "calculated": bool(items),
            "reason": None,
            "evidence": {"network_flows": len(flows), "open_findings": len(alerts)},
        }
    finally:
        connection.close()
