import secrets
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_db_connection


router = APIRouter(
    prefix="/api/sensors",
    tags=["Sensors"],
)


class SensorEnrollmentRequest(BaseModel):
    company_id: int
    sensor_name: str
    environment_name: str
    environment_type: str = "infrastructure"


@router.post("/enroll")
def create_sensor_enrollment(request: SensorEnrollmentRequest):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        # ---------------------------------------------------------
        # Verify organization/company
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                id,
                company_name,
                industry,
                country,
                email,
                phone,
                website,
                subscription_plan,
                status
            FROM companies
            WHERE id = %s
            """,
            (request.company_id,),
        )

        company = cursor.fetchone()

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found.",
            )

        # ---------------------------------------------------------
        # Generate secure enrollment token
        # ---------------------------------------------------------
        enrollment_token = secrets.token_urlsafe(32)

        now = datetime.utcnow()

        # ---------------------------------------------------------
        # Create sensor enrollment
        # ---------------------------------------------------------
        cursor.execute(
            """
            INSERT INTO sensor_enrollments (
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                enrollment_token,
                status,
                created_at,
                updated_at,
                registered_at,
                last_heartbeat,
                last_status_change
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                NULL,
                NULL,
                %s
            )
            RETURNING
                id,
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                enrollment_token,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            """,
            (
                request.company_id,
                request.sensor_name,
                request.environment_name,
                request.environment_type,
                enrollment_token,
                "PENDING",
                now,
                now,
                now,
            ),
        )

        enrollment = cursor.fetchone()

        connection.commit()

        return {
            "success": True,
            "message": "Sensor enrollment created successfully.",
            "company": {
                "id": company["id"],
                "name": company["company_name"],
            },
            "enrollment": enrollment,
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to create sensor enrollment: {error}",
        )

    finally:
        connection.close()


@router.get("/{company_id}")
def get_company_sensors(company_id: int):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            FROM sensor_enrollments
            WHERE company_id = %s
            ORDER BY created_at DESC
            """,
            (company_id,),
        )

        sensors = cursor.fetchall()

        return {
            "success": True,
            "company_id": company_id,
            "sensors": sensors,
        }

    finally:
        connection.close()


@router.post("/register")
def register_sensor(enrollment_token: str):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            FROM sensor_enrollments
            WHERE enrollment_token = %s
            """,
            (enrollment_token,),
        )

        enrollment = cursor.fetchone()

        if not enrollment:
            raise HTTPException(
                status_code=404,
                detail="Invalid enrollment token.",
            )

        if enrollment["status"] == "ONLINE":
            return {
                "success": True,
                "message": "Sensor is already online.",
                "sensor": enrollment,
            }

        now = datetime.utcnow()

        cursor.execute(
            """
            UPDATE sensor_enrollments
            SET
                status = 'REGISTERED',
                registered_at = COALESCE(registered_at, %s),
                updated_at = %s,
                last_status_change = %s
            WHERE id = %s
            RETURNING
                id,
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            """,
            (
                now,
                now,
                now,
                enrollment["id"],
            ),
        )

        sensor = cursor.fetchone()

        connection.commit()

        return {
            "success": True,
            "message": "Sensor registered successfully.",
            "sensor": sensor,
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to register sensor: {error}",
        )

    finally:
        connection.close()


@router.post("/heartbeat")
def sensor_heartbeat(enrollment_token: str):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            FROM sensor_enrollments
            WHERE enrollment_token = %s
            """,
            (enrollment_token,),
        )

        enrollment = cursor.fetchone()

        if not enrollment:
            raise HTTPException(
                status_code=404,
                detail="Invalid enrollment token.",
            )

        now = datetime.utcnow()

        status_changed = enrollment["status"] != "ONLINE"

        cursor.execute(
            """
            UPDATE sensor_enrollments
            SET
                status = 'ONLINE',
                registered_at = COALESCE(registered_at, %s),
                last_heartbeat = %s,
                last_status_change =
                    CASE
                        WHEN %s THEN %s
                        ELSE last_status_change
                    END,
                updated_at = %s
            WHERE id = %s
            RETURNING
                id,
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            """,
            (
                now,
                now,
                status_changed,
                now,
                now,
                enrollment["id"],
            ),
        )

        sensor = cursor.fetchone()

        connection.commit()

        return {
            "success": True,
            "message": "Heartbeat received.",
            "sensor": sensor,
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to process sensor heartbeat: {error}",
        )

    finally:
        connection.close()


@router.get("/enrollment/{enrollment_id}/status")
def get_enrollment_status(enrollment_id: int):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                company_id,
                sensor_name,
                environment_name,
                environment_type,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            FROM sensor_enrollments
            WHERE id = %s
            """,
            (enrollment_id,),
        )

        enrollment = cursor.fetchone()

        if not enrollment:
            raise HTTPException(
                status_code=404,
                detail="Sensor enrollment not found.",
            )

        return {
            "success": True,
            "enrollment": enrollment,
        }

    finally:
        connection.close()