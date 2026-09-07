import secrets
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from database import get_db_connection

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])

class SensorEnrollmentRequest(BaseModel):
    sensor_name: str = Field(..., min_length=1, max_length=255)
    environment_name: str = Field(..., min_length=1, max_length=255)
    environment_type: str = Field(default="infrastructure", max_length=100)

class TelemetryEnvelope(BaseModel):
    telemetry_type: str = Field(..., min_length=1, max_length=80)
    payload: dict = Field(default_factory=dict)

@router.post("/enroll")
def create_sensor_enrollment(request: SensorEnrollmentRequest, current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None: raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor=connection.cursor(); company_id=current_user["company_id"]
        cursor.execute("SELECT id, company_name FROM companies WHERE id=%s", (company_id,)); company=cursor.fetchone()
        if not company: raise HTTPException(status_code=404, detail="Company not found.")
        sensor_name=request.sensor_name.strip(); environment_name=request.environment_name.strip(); environment_type=request.environment_type.strip() or "infrastructure"
        if not sensor_name or not environment_name: raise HTTPException(status_code=400, detail="Sensor and environment names are required.")
        token=secrets.token_urlsafe(32); now=datetime.utcnow()
        cursor.execute("""INSERT INTO sensor_enrollments (company_id,sensor_name,environment_name,environment_type,enrollment_token,status,created_at,updated_at,last_status_change)
        VALUES (%s,%s,%s,%s,%s,'PENDING',%s,%s,%s) RETURNING id,company_id,sensor_name,environment_name,environment_type,enrollment_token,status,registered_at,last_heartbeat,last_status_change,created_at,updated_at""",(company_id,sensor_name,environment_name,environment_type,token,now,now,now))
        enrollment=cursor.fetchone(); connection.commit()
        return {"success":True,"message":"Sensor enrollment created successfully.","company":{"id":company["id"],"name":company["company_name"]},"enrollment":enrollment}
    except HTTPException: connection.rollback(); raise
    except Exception as error: connection.rollback(); raise HTTPException(status_code=500, detail="Unable to create sensor enrollment.") from error
    finally: connection.close()

@router.get("")
@router.get("/")
def get_company_sensors(current_user: dict = Depends(get_current_user)):
    connection=get_db_connection()
    if connection is None: raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor=connection.cursor(); cursor.execute("SELECT id,company_id,sensor_name,environment_name,environment_type,status,registered_at,last_heartbeat,last_status_change,created_at,updated_at FROM sensor_enrollments WHERE company_id=%s ORDER BY created_at DESC",(current_user["company_id"],))
        return {"success":True,"company_id":current_user["company_id"],"sensors":cursor.fetchall()}
    finally: connection.close()

@router.post("/register")
def register_sensor(enrollment_token:str):
    connection=get_db_connection()
    if connection is None: raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor=connection.cursor(); cursor.execute("SELECT id,company_id,sensor_name,environment_name,environment_type,status,registered_at,last_heartbeat,last_status_change,created_at,updated_at FROM sensor_enrollments WHERE enrollment_token=%s",(enrollment_token,)); enrollment=cursor.fetchone()
        if not enrollment: raise HTTPException(status_code=404, detail="Invalid enrollment token.")
        if enrollment["status"]=="ONLINE": return {"success":True,"message":"Sensor is already online.","sensor":enrollment}
        now=datetime.utcnow(); cursor.execute("""UPDATE sensor_enrollments SET status='REGISTERED',registered_at=COALESCE(registered_at,%s),updated_at=%s,last_status_change=%s WHERE id=%s RETURNING id,company_id,sensor_name,environment_name,environment_type,status,registered_at,last_heartbeat,last_status_change,created_at,updated_at""",(now,now,now,enrollment["id"]))
        sensor=cursor.fetchone(); connection.commit(); return {"success":True,"message":"Sensor registered successfully.","sensor":sensor}
    except HTTPException: connection.rollback(); raise
    except Exception as error: connection.rollback(); raise HTTPException(status_code=500, detail="Unable to register sensor.") from error
    finally: connection.close()

@router.post("/heartbeat")
def sensor_heartbeat(enrollment_token:str):
    connection=get_db_connection()
    if connection is None: raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor=connection.cursor(); cursor.execute("SELECT id,company_id,sensor_name,environment_name,environment_type,status,registered_at,last_heartbeat,last_status_change,created_at,updated_at FROM sensor_enrollments WHERE enrollment_token=%s",(enrollment_token,)); enrollment=cursor.fetchone()
        if not enrollment: raise HTTPException(status_code=404, detail="Invalid enrollment token.")
        now=datetime.utcnow(); changed=enrollment["status"]!="ONLINE"
        cursor.execute("""UPDATE sensor_enrollments SET status='ONLINE',registered_at=COALESCE(registered_at,%s),last_heartbeat=%s,last_status_change=CASE WHEN %s THEN %s ELSE last_status_change END,updated_at=%s WHERE id=%s RETURNING id,company_id,sensor_name,environment_name,environment_type,status,registered_at,last_heartbeat,last_status_change,created_at,updated_at""",(now,now,changed,now,now,enrollment["id"]))
        sensor=cursor.fetchone(); connection.commit(); return {"success":True,"message":"Heartbeat received.","sensor":sensor}
    except HTTPException: connection.rollback(); raise
    except Exception as error: connection.rollback(); raise HTTPException(status_code=500, detail="Unable to process sensor heartbeat.") from error
    finally: connection.close()

@router.post("/telemetry")
def ingest_telemetry(enrollment_token:str,envelope:TelemetryEnvelope):
    """Authorized sensor ingestion. The enrollment token identifies the enrolled device."""
    connection=get_db_connection()
    if connection is None: raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        cursor=connection.cursor(); cursor.execute("SELECT id,company_id,status FROM sensor_enrollments WHERE enrollment_token=%s",(enrollment_token,)); sensor=cursor.fetchone()
        if not sensor: raise HTTPException(status_code=401, detail="Invalid enrollment token.")
        if sensor["status"] not in {"REGISTERED","ONLINE"}: raise HTTPException(status_code=409, detail="Sensor must be registered before telemetry can be accepted.")
        cursor.execute("INSERT INTO sensor_telemetry (sensor_id,company_id,telemetry_type,payload) VALUES (%s,%s,%s,%s) RETURNING id,received_at",(sensor["id"],sensor["company_id"],envelope.telemetry_type,json.dumps(envelope.payload)))
        stored=cursor.fetchone(); cursor.execute("UPDATE sensor_enrollments SET status='ONLINE',last_heartbeat=CURRENT_TIMESTAMP,updated_at=CURRENT_TIMESTAMP WHERE id=%s",(sensor["id"],))
        cursor.execute("INSERT INTO security_timeline (company_id,event_type,severity,subject_type,subject_key,message,source,metadata) VALUES (%s,'sensor_telemetry','INFO','sensor',%s,%s,'sensor',%s)",(sensor["company_id"],str(sensor["id"]),f"Sensor telemetry received: {envelope.telemetry_type}",json.dumps(envelope.payload)))
        connection.commit(); return {"success":True,"accepted":True,"telemetry":stored}
    except HTTPException: connection.rollback(); raise
    except Exception as error: connection.rollback(); raise HTTPException(status_code=500, detail="Unable to ingest sensor telemetry.") from error
    finally: connection.close()

@router.get("/enrollment/{enrollment_id}/status")
def get_enrollment_status(enrollment_id:int,current_user:dict=Depends(get_current_user)):
    connection=get_db_connection()
    if connection is None: raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor=connection.cursor(); cursor.execute("SELECT id,company_id,sensor_name,environment_name,environment_type,status,registered_at,last_heartbeat,last_status_change,created_at,updated_at FROM sensor_enrollments WHERE id=%s AND company_id=%s",(enrollment_id,current_user["company_id"]))
        enrollment=cursor.fetchone()
        if not enrollment: raise HTTPException(status_code=404, detail="Sensor enrollment not found.")
        cursor.execute("SELECT COUNT(*) AS count FROM sensor_telemetry WHERE sensor_id=%s",(enrollment_id,)); telemetry_count=cursor.fetchone()["count"]
        return {"success":True,"enrollment":enrollment,"telemetry_count":telemetry_count}
    finally: connection.close()
