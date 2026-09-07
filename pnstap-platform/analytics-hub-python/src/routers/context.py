from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from database import get_db_connection

router = APIRouter(prefix="/api/context", tags=["Security Context"])


def db_or_503():
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    return connection


class InvestigationCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    priority: str = Field(default="MEDIUM", max_length=20)
    source_alert_id: int | None = None
    summary: str | None = None


class InvestigationEventCreate(BaseModel):
    event_type: str = Field(..., min_length=2, max_length=80)
    message: str = Field(..., min_length=1, max_length=4000)


class AssetUpsert(BaseModel):
    asset_key: str = Field(..., min_length=1, max_length=255)
    asset_name: str = Field(..., min_length=1, max_length=255)
    asset_type: str = Field(default="unknown", max_length=80)
    environment_name: str | None = None
    criticality: str = Field(default="MEDIUM", max_length=20)
    exposure: str = Field(default="INTERNAL", max_length=30)
    source: str = Field(default="sensor", max_length=80)
    metadata: dict = Field(default_factory=dict)


class IdentityEventCreate(BaseModel):
    identity_key: str = Field(..., min_length=1, max_length=255)
    event_type: str = Field(..., min_length=2, max_length=100)
    risk_score: int = Field(default=0, ge=0, le=100)
    source: str = Field(default="sensor", max_length=80)
    metadata: dict = Field(default_factory=dict)


class DriftCreate(BaseModel):
    subject_type: str = Field(..., max_length=80)
    subject_key: str = Field(..., max_length=255)
    change_type: str = Field(..., max_length=80)
    severity: str = Field(default="MEDIUM", max_length=20)
    before_state: dict = Field(default_factory=dict)
    after_state: dict = Field(default_factory=dict)
    source: str = Field(default="sensor", max_length=80)


@router.get("/summary")
def context_summary(current_user: dict = Depends(get_current_user)):
    company_id = current_user["company_id"]
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            counts = {}
            for key, table in {
                "assets": "asset_registry",
                "identities": "identity_events",
                "investigations": "investigations",
                "evidence": "evidence",
                "timeline": "security_timeline",
                "drift": "drift_events",
            }.items():
                cursor.execute(f"SELECT COUNT(*) AS count FROM {table} WHERE company_id = %s", (company_id,))
                counts[key] = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) AS count FROM alerts WHERE company_id = %s AND LOWER(status) = 'open'", (company_id,))
            counts["open_alerts"] = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) AS count FROM sensor_enrollments WHERE company_id = %s AND status = 'ONLINE'", (company_id,))
            counts["online_sensors"] = cursor.fetchone()["count"]
            return {"success": True, "summary": counts}
    finally:
        connection.close()


@router.get("/assets")
def assets(current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, asset_key, asset_name, asset_type, environment_name,
                       criticality, exposure, source, metadata, first_seen, last_seen
                FROM asset_registry WHERE company_id = %s ORDER BY last_seen DESC LIMIT 500
            """, (current_user["company_id"],))
            return {"success": True, "assets": cursor.fetchall()}
    finally:
        connection.close()


@router.post("/assets")
def upsert_asset(payload: AssetUpsert, current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO asset_registry
                    (company_id, asset_key, asset_name, asset_type, environment_name,
                     criticality, exposure, source, metadata)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (company_id, asset_key) DO UPDATE SET
                    asset_name=EXCLUDED.asset_name, asset_type=EXCLUDED.asset_type,
                    environment_name=EXCLUDED.environment_name, criticality=EXCLUDED.criticality,
                    exposure=EXCLUDED.exposure, source=EXCLUDED.source,
                    metadata=EXCLUDED.metadata, last_seen=CURRENT_TIMESTAMP
                RETURNING *
            """, (current_user["company_id"], payload.asset_key, payload.asset_name,
                  payload.asset_type, payload.environment_name, payload.criticality,
                  payload.exposure, payload.source, json.dumps(payload.metadata)))
            asset = cursor.fetchone()
            cursor.execute("""
                INSERT INTO security_timeline (company_id,event_type,severity,subject_type,subject_key,message,source,metadata)
                VALUES (%s,'asset_observed','INFO','asset',%s,%s,%s,%s)
            """, (current_user["company_id"], payload.asset_key,
                  f"Asset observed: {payload.asset_name}", payload.source, json.dumps(payload.metadata)))
            connection.commit()
            return {"success": True, "asset": asset}
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to record asset.") from error
    finally:
        connection.close()


@router.get("/identities")
def identities(current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, identity_key, event_type, source, risk_score, metadata, observed_at
                FROM identity_events WHERE company_id = %s ORDER BY observed_at DESC LIMIT 500
            """, (current_user["company_id"],))
            return {"success": True, "identities": cursor.fetchall()}
    finally:
        connection.close()


@router.post("/identities/events")
def identity_event(payload: IdentityEventCreate, current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO identity_events (company_id,identity_key,event_type,source,risk_score,metadata)
                VALUES (%s,%s,%s,%s,%s,%s) RETURNING *
            """, (current_user["company_id"], payload.identity_key, payload.event_type,
                  payload.source, payload.risk_score, json.dumps(payload.metadata)))
            event = cursor.fetchone()
            cursor.execute("""
                INSERT INTO security_timeline (company_id,event_type,severity,subject_type,subject_key,message,source,metadata)
                VALUES (%s,'identity_event',%s,'identity',%s,%s,%s,%s)
            """, (current_user["company_id"],
                  "HIGH" if payload.risk_score >= 75 else "MEDIUM" if payload.risk_score >= 40 else "INFO",
                  payload.identity_key, payload.event_type, payload.source, json.dumps(payload.metadata)))
            connection.commit()
            return {"success": True, "event": event}
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to record identity event.") from error
    finally:
        connection.close()


@router.get("/investigations")
def investigations(current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT i.id, i.title, i.status, i.priority, i.summary, i.source_alert_id,
                       i.owner_user_id, i.created_at, i.updated_at, i.resolved_at,
                       COALESCE(e.event_count,0) AS event_count,
                       COALESCE(ev.evidence_count,0) AS evidence_count
                FROM investigations i
                LEFT JOIN (SELECT investigation_id, COUNT(*) event_count FROM investigation_events GROUP BY investigation_id) e ON e.investigation_id=i.id
                LEFT JOIN (SELECT investigation_id, COUNT(*) evidence_count FROM evidence WHERE investigation_id IS NOT NULL GROUP BY investigation_id) ev ON ev.investigation_id=i.id
                WHERE i.company_id=%s ORDER BY i.updated_at DESC LIMIT 200
            """, (current_user["company_id"],))
            return {"success": True, "investigations": cursor.fetchall()}
    finally:
        connection.close()


@router.post("/investigations")
def create_investigation(payload: InvestigationCreate, current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            if payload.source_alert_id:
                cursor.execute("SELECT id FROM alerts WHERE id=%s AND company_id=%s", (payload.source_alert_id,current_user["company_id"]))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail="Source alert not found in this workspace.")
            cursor.execute("""
                INSERT INTO investigations (company_id,title,priority,source_alert_id,summary,owner_user_id)
                VALUES (%s,%s,%s,%s,%s,%s) RETURNING *
            """, (current_user["company_id"], payload.title, payload.priority.upper(),
                  payload.source_alert_id, payload.summary, current_user["user_id"]))
            investigation = cursor.fetchone()
            cursor.execute("""
                INSERT INTO investigation_events (investigation_id,company_id,event_type,actor_user_id,message)
                VALUES (%s,%s,'created',%s,%s)
            """, (investigation["id"], current_user["company_id"], current_user["user_id"], "Investigation opened"))
            cursor.execute("""
                INSERT INTO security_timeline (company_id,event_type,severity,subject_type,subject_key,message,source,metadata)
                VALUES (%s,'investigation_created','INFO','investigation',%s,%s,'platform',%s)
            """, (current_user["company_id"], str(investigation["id"]), payload.title, json.dumps({"priority": payload.priority.upper()})))
            connection.commit()
            return {"success": True, "investigation": investigation}
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to create investigation.") from error
    finally:
        connection.close()


@router.get("/investigations/{investigation_id}")
def investigation_detail(investigation_id: int, current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM investigations WHERE id=%s AND company_id=%s", (investigation_id,current_user["company_id"]))
            investigation = cursor.fetchone()
            if not investigation:
                raise HTTPException(status_code=404, detail="Investigation not found.")
            cursor.execute("SELECT * FROM investigation_events WHERE investigation_id=%s AND company_id=%s ORDER BY created_at DESC", (investigation_id,current_user["company_id"]))
            events = cursor.fetchall()
            cursor.execute("SELECT * FROM evidence WHERE investigation_id=%s AND company_id=%s ORDER BY observed_at DESC", (investigation_id,current_user["company_id"]))
            evidence_rows = cursor.fetchall()
            return {"success": True, "investigation": investigation, "events": events, "evidence": evidence_rows}
    finally:
        connection.close()


@router.post("/investigations/{investigation_id}/events")
def add_investigation_event(investigation_id: int, payload: InvestigationEventCreate, current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM investigations WHERE id=%s AND company_id=%s", (investigation_id,current_user["company_id"]))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Investigation not found.")
            cursor.execute("""
                INSERT INTO investigation_events (investigation_id,company_id,event_type,actor_user_id,message)
                VALUES (%s,%s,%s,%s,%s) RETURNING *
            """, (investigation_id,current_user["company_id"],payload.event_type,current_user["user_id"],payload.message))
            event = cursor.fetchone()
            cursor.execute("UPDATE investigations SET updated_at=CURRENT_TIMESTAMP WHERE id=%s", (investigation_id,))
            connection.commit()
            return {"success": True, "event": event}
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to add investigation event.") from error
    finally:
        connection.close()


@router.get("/timeline")
def timeline(current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id,event_type,severity,subject_type,subject_key,message,source,metadata,occurred_at FROM security_timeline WHERE company_id=%s ORDER BY occurred_at DESC LIMIT 500", (current_user["company_id"],))
            return {"success": True, "events": cursor.fetchall()}
    finally:
        connection.close()


@router.get("/drift")
def drift(current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id,subject_type,subject_key,change_type,severity,before_state,after_state,source,detected_at FROM drift_events WHERE company_id=%s ORDER BY detected_at DESC LIMIT 500", (current_user["company_id"],))
            return {"success": True, "events": cursor.fetchall()}
    finally:
        connection.close()


@router.post("/drift")
def record_drift(payload: DriftCreate, current_user: dict = Depends(get_current_user)):
    connection = db_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO drift_events (company_id,subject_type,subject_key,change_type,severity,before_state,after_state,source)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *
            """, (current_user["company_id"],payload.subject_type,payload.subject_key,payload.change_type,
                  payload.severity.upper(),json.dumps(payload.before_state),json.dumps(payload.after_state),payload.source))
            event = cursor.fetchone()
            cursor.execute("""
                INSERT INTO security_timeline (company_id,event_type,severity,subject_type,subject_key,message,source,metadata)
                VALUES (%s,'security_drift',%s,%s,%s,%s,%s,%s)
            """, (current_user["company_id"],payload.severity.upper(),payload.subject_type,payload.subject_key,
                  f"{payload.change_type} detected on {payload.subject_key}",payload.source,json.dumps({"before":payload.before_state,"after":payload.after_state})))
            connection.commit()
            return {"success": True, "drift": event}
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to record security drift.") from error
    finally:
        connection.close()
