import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from database import get_db_connection


router = APIRouter(
    prefix="/api/sensors",
    tags=["Sensors"],
)


class SensorEnrollmentRequest(BaseModel):
    sensor_name: str = Field(..., min_length=1, max_length=255)
    environment_name: str = Field(..., min_length=1, max_length=255)
    environment_type: str = Field(default="infrastructure", max_length=100)


@router.post("/enroll")
def create_sensor_enrollment(
    request: SensorEnrollmentRequest,
    current_user: dict = Depends(get_current_user),
):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        cursor = connection.cursor()
        company_id = current_user["company_id"]

        cursor.execute(
            "SELECT id, company_name FROM companies WHERE id = %s",
            (company_id,),
        )
        company = cursor.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found.")

        sensor_name = request.sensor_name.strip()
        environment_name = request.environment_name.strip()
        environment_type = request.environment_type.strip() or "infrastructure"
        if not sensor_name or not environment_name:
            raise HTTPException(status_code=400, detail="Sensor and environment names are required.")

        enrollment_token = secrets.token_urlsafe(32)
        now = datetime.utcnow()

        cursor.execute(
            """
            INSERT INTO sensor_enrollments (
                company_id, sensor_name, environment_name, environment_type,
                enrollment_token, status, created_at, updated_at,
                registered_at, last_heartbeat, last_status_change
            )
            VALUES (%s, %s, %s, %s, %s, 'PENDING', %s, %s, NULL, NULL, %s)
            RETURNING id, company_id, sensor_name, environment_name,
                      environment_type, enrollment_token, status,
                      registered_at, last_heartbeat, last_status_change,
                      created_at, updated_at
            """,
            (company_id, sensor_name, environment_name, environment_type,
             enrollment_token, now, now, now),
        )
        enrollment = cursor.fetchone()
        connection.commit()

        return {
            "success": True,
            "message": "Sensor enrollment created successfully.",
            "company": {"id": company["id"], "name": company["company_name"]},
            "enrollment": enrollment,
        }
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to create sensor enrollment.") from error
    finally:
        connection.close()


@router.get("")
@router.get("/")
def get_company_sensors(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, company_id, sensor_name, environment_name,
                   environment_type, status, registered_at, last_heartbeat,
                   last_status_change, created_at, updated_at
            FROM sensor_enrollments
            WHERE company_id = %s
            ORDER BY created_at DESC
            """,
            (current_user["company_id"],),
        )
        return {
            "success": True,
            "company_id": current_user["company_id"],
            "sensors": cursor.fetchall(),
        }
    finally:
        connection.close()


@router.post("/register")
def register_sensor(enrollment_token: str):
    """Sensor-agent endpoint: the enrollment token acts as the device credential."""
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, company_id, sensor_name, environment_name,
                   environment_type, status, registered_at, last_heartbeat,
                   last_status_change, created_at, updated_at
            FROM sensor_enrollments
            WHERE enrollment_token = %s
            """,
            (enrollment_token,),
        )
        enrollment = cursor.fetchone()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Invalid enrollment token.")

        if enrollment["status"] == "ONLINE":
            return {"success": True, "message": "Sensor is already online.", "sensor": enrollment}

        now = datetime.utcnow()
        cursor.execute(
            """
            UPDATE sensor_enrollments
            SET status = 'REGISTERED',
                registered_at = COALESCE(registered_at, %s),
                updated_at = %s,
                last_status_change = %s
            WHERE id = %s
            RETURNING id, company_id, sensor_name, environment_name,
                      environment_type, status, registered_at, last_heartbeat,
                      last_status_change, created_at, updated_at
            """,
            (now, now, now, enrollment["id"]),
        )
        sensor = cursor.fetchone()
        connection.commit()
        return {"success": True, "message": "Sensor registered successfully.", "sensor": sensor}
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to register sensor.") from error
    finally:
        connection.close()


@router.post("/heartbeat")
def sensor_heartbeat(enrollment_token: str):
    """Sensor-agent endpoint authenticated by its enrollment token."""
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, company_id, sensor_name, environment_name, environment_type, status, registered_at, last_heartbeat, last_status_change, created_at, updated_at FROM sensor_enrollments WHERE enrollment_token = %s",
            (enrollment_token,),
        )
        enrollment = cursor.fetchone()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Invalid enrollment token.")

        now = datetime.utcnow()
        status_changed = enrollment["status"] != "ONLINE"
        cursor.execute(
            """
            UPDATE sensor_enrollments
            SET status = 'ONLINE',
                registered_at = COALESCE(registered_at, %s),
                last_heartbeat = %s,
                last_status_change = CASE WHEN %s THEN %s ELSE last_status_change END,
                updated_at = %s
            WHERE id = %s
            RETURNING id, company_id, sensor_name, environment_name,
                      environment_type, status, registered_at, last_heartbeat,
                      last_status_change, created_at, updated_at
            """,
            (now, now, status_changed, now, now, enrollment["id"]),
        )
        sensor = cursor.fetchone()
        connection.commit()
        return {"success": True, "message": "Heartbeat received.", "sensor": sensor}
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to process sensor heartbeat.") from error
    finally:
        connection.close()


@router.get("/enrollment/{enrollment_id}/status")
def get_enrollment_status(
    enrollment_id: int,
    current_user: dict = Depends(get_current_user),
):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, company_id, sensor_name, environment_name,
                   environment_type, status, registered_at, last_heartbeat,
                   last_status_change, created_at, updated_at
            FROM sensor_enrollments
            WHERE id = %s AND company_id = %s
            """,
            (enrollment_id, current_user["company_id"]),
        )
        enrollment = cursor.fetchone()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Sensor enrollment not found.")
        return {"success": True, "enrollment": enrollment}
    finally:
        connection.close()
