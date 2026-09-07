import secrets
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_db_connection


router = APIRouter(
    prefix="/api/integrations",
    tags=["Integrations"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class CloudIntegrationRequest(BaseModel):
    company_id: int
    connection_name: str
    environment_name: str
    environment_type: str = "infrastructure"
    provider: str


class APIIntegrationRequest(BaseModel):
    company_id: int
    connection_name: str
    environment_name: str
    environment_type: str = "infrastructure"
    api_platform: str
    api_url: str


# ============================================================
# DATABASE SETUP
# ============================================================

def ensure_integrations_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS security_integrations (
            id BIGSERIAL PRIMARY KEY,
            company_id BIGINT NOT NULL,
            connection_name VARCHAR(255) NOT NULL,
            environment_name VARCHAR(255) NOT NULL,
            environment_type VARCHAR(100) NOT NULL DEFAULT 'infrastructure',

            integration_type VARCHAR(50) NOT NULL,

            provider VARCHAR(100),
            api_platform VARCHAR(100),
            api_url TEXT,

            enrollment_token VARCHAR(255) NOT NULL UNIQUE,

            status VARCHAR(50) NOT NULL DEFAULT 'PENDING',

            registered_at TIMESTAMP NULL,
            last_heartbeat TIMESTAMP NULL,
            last_status_change TIMESTAMP NOT NULL,

            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        """
    )


# ============================================================
# COMPANY VALIDATION
# ============================================================

def get_company(cursor, company_id):
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
        (company_id,),
    )

    return cursor.fetchone()


# ============================================================
# CLOUD CONNECTION
# ============================================================

@router.post("/cloud")
def create_cloud_integration(
    request: CloudIntegrationRequest
):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        ensure_integrations_table(cursor)

        company = get_company(
            cursor,
            request.company_id,
        )

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found.",
            )

        provider = request.provider.strip().lower()

        if provider not in {
            "aws",
            "azure",
            "gcp",
        }:
            raise HTTPException(
                status_code=400,
                detail="Unsupported cloud provider.",
            )

        connection_name = (
            request.connection_name.strip()
        )

        environment_name = (
            request.environment_name.strip()
        )

        if not connection_name:
            raise HTTPException(
                status_code=400,
                detail="Connection name is required.",
            )

        if not environment_name:
            raise HTTPException(
                status_code=400,
                detail="Environment name is required.",
            )

        enrollment_token = (
            "CYPHERIS-CLOUD_"
            + secrets.token_hex(16).upper()
        )

        now = datetime.utcnow()

        cursor.execute(
            """
            INSERT INTO security_integrations (
                company_id,
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                provider,
                api_platform,
                api_url,
                enrollment_token,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                'CLOUD',
                %s,
                NULL,
                NULL,
                %s,
                'PENDING',
                NULL,
                NULL,
                %s,
                %s,
                %s
            )
            RETURNING
                id,
                company_id,
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                provider,
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
                connection_name,
                environment_name,
                request.environment_type,
                provider,
                enrollment_token,
                now,
                now,
                now,
            ),
        )

        integration = cursor.fetchone()

        connection.commit()

        return {
            "success": True,
            "message": "Cloud connection created successfully.",
            "company": {
                "id": company["id"],
                "name": company["company_name"],
            },
            "integration": integration,
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        print(
            "CLOUD INTEGRATION ERROR:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to create cloud connection: "
                f"{error}"
            ),
        )

    finally:
        connection.close()


# ============================================================
# SECURITY API CONNECTION
# ============================================================

@router.post("/api")
def create_api_integration(
    request: APIIntegrationRequest
):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        ensure_integrations_table(cursor)

        company = get_company(
            cursor,
            request.company_id,
        )

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found.",
            )

        api_platform = (
            request.api_platform.strip().lower()
        )

        if api_platform not in {
            "siem",
            "edr",
            "custom",
        }:
            raise HTTPException(
                status_code=400,
                detail="Unsupported security API platform.",
            )

        connection_name = (
            request.connection_name.strip()
        )

        environment_name = (
            request.environment_name.strip()
        )

        api_url = request.api_url.strip()

        if not connection_name:
            raise HTTPException(
                status_code=400,
                detail="Connection name is required.",
            )

        if not environment_name:
            raise HTTPException(
                status_code=400,
                detail="Environment name is required.",
            )

        if not api_url:
            raise HTTPException(
                status_code=400,
                detail="Security API URL is required.",
            )

        enrollment_token = (
            "CYPHERIS-API_"
            + secrets.token_hex(16).upper()
        )

        now = datetime.utcnow()

        cursor.execute(
            """
            INSERT INTO security_integrations (
                company_id,
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                provider,
                api_platform,
                api_url,
                enrollment_token,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                'API',
                NULL,
                %s,
                %s,
                %s,
                'PENDING',
                NULL,
                NULL,
                %s,
                %s,
                %s
            )
            RETURNING
                id,
                company_id,
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                api_platform,
                api_url,
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
                connection_name,
                environment_name,
                request.environment_type,
                api_platform,
                api_url,
                enrollment_token,
                now,
                now,
                now,
            ),
        )

        integration = cursor.fetchone()

        connection.commit()

        return {
            "success": True,
            "message": "Security API connection created successfully.",
            "company": {
                "id": company["id"],
                "name": company["company_name"],
            },
            "integration": integration,
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        print(
            "API INTEGRATION ERROR:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to create API connection: "
                f"{error}"
            ),
        )

    finally:
        connection.close()


# ============================================================
# GET COMPANY INTEGRATIONS
# ============================================================

@router.get("/company/{company_id}")
def get_company_integrations(company_id: int):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        ensure_integrations_table(cursor)

        company = get_company(
            cursor,
            company_id,
        )

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found.",
            )

        cursor.execute(
            """
            SELECT
                id,
                company_id,
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                provider,
                api_platform,
                api_url,
                enrollment_token,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            FROM security_integrations
            WHERE company_id = %s
            ORDER BY created_at DESC
            """,
            (company_id,),
        )

        integrations = cursor.fetchall()

        return {
            "success": True,
            "company_id": company_id,
            "integrations": integrations,
        }

    finally:
        connection.close()


# ============================================================
# GET SINGLE INTEGRATION STATUS
# ============================================================

@router.get("/{integration_id}/status")
def get_integration_status(
    integration_id: int
):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        ensure_integrations_table(cursor)

        cursor.execute(
            """
            SELECT
                id,
                company_id,
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                provider,
                api_platform,
                api_url,
                enrollment_token,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            FROM security_integrations
            WHERE id = %s
            """,
            (integration_id,),
        )

        integration = cursor.fetchone()

        if not integration:
            raise HTTPException(
                status_code=404,
                detail="Security integration not found.",
            )

        return {
            "success": True,
            "integration": integration,
        }

    finally:
        connection.close()


# ============================================================
# REGISTER CLOUD / API CONNECTION
# ============================================================

@router.post("/register")
def register_integration(
    enrollment_token: str
):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        ensure_integrations_table(cursor)

        cursor.execute(
            """
            SELECT
                id,
                company_id,
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                provider,
                api_platform,
                api_url,
                enrollment_token,
                status,
                registered_at,
                last_heartbeat,
                last_status_change,
                created_at,
                updated_at
            FROM security_integrations
            WHERE enrollment_token = %s
            """,
            (enrollment_token,),
        )

        integration = cursor.fetchone()

        if not integration:
            raise HTTPException(
                status_code=404,
                detail="Invalid integration credential.",
            )

        now = datetime.utcnow()

        cursor.execute(
            """
            UPDATE security_integrations
            SET
                status = 'REGISTERED',
                registered_at =
                    COALESCE(registered_at, %s),
                updated_at = %s,
                last_status_change = %s
            WHERE id = %s
            RETURNING
                id,
                company_id,
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                provider,
                api_platform,
                api_url,
                enrollment_token,
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
                integration["id"],
            ),
        )

        updated = cursor.fetchone()

        connection.commit()

        return {
            "success": True,
            "message": "Integration registered successfully.",
            "integration": updated,
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to register integration: "
                f"{error}"
            ),
        )

    finally:
        connection.close()


# ============================================================
# INTEGRATION HEARTBEAT
# ============================================================

@router.post("/heartbeat")
def integration_heartbeat(
    enrollment_token: str
):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    try:
        cursor = connection.cursor()

        ensure_integrations_table(cursor)

        cursor.execute(
            """
            SELECT
                id,
                status
            FROM security_integrations
            WHERE enrollment_token = %s
            """,
            (enrollment_token,),
        )

        integration = cursor.fetchone()

        if not integration:
            raise HTTPException(
                status_code=404,
                detail="Invalid integration credential.",
            )

        now = datetime.utcnow()

        status_changed = (
            integration["status"] != "ONLINE"
        )

        cursor.execute(
            """
            UPDATE security_integrations
            SET
                status = 'ONLINE',
                registered_at =
                    COALESCE(registered_at, %s),
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
                connection_name,
                environment_name,
                environment_type,
                integration_type,
                provider,
                api_platform,
                api_url,
                enrollment_token,
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
                integration["id"],
            ),
        )

        updated = cursor.fetchone()

        connection.commit()

        return {
            "success": True,
            "message": "Integration heartbeat received.",
            "integration": updated,
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process integration heartbeat: "
                f"{error}"
            ),
        )

    finally:
        connection.close()