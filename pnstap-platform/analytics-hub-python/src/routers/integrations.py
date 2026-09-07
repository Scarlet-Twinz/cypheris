import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from auth import get_current_user
from database import get_db_connection

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])


class CloudIntegrationRequest(BaseModel):
    connection_name: str = Field(..., min_length=1, max_length=255)
    environment_name: str = Field(..., min_length=1, max_length=255)
    environment_type: str = Field(default="infrastructure", max_length=100)
    provider: str = Field(..., min_length=2, max_length=50)


class APIIntegrationRequest(BaseModel):
    connection_name: str = Field(..., min_length=1, max_length=255)
    environment_name: str = Field(..., min_length=1, max_length=255)
    environment_type: str = Field(default="infrastructure", max_length=100)
    api_platform: str = Field(..., min_length=2, max_length=50)
    api_url: HttpUrl


def ensure_integrations_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS security_integrations (
            id BIGSERIAL PRIMARY KEY,
            company_id BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
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


def get_company(cursor, company_id):
    cursor.execute("SELECT id, company_name FROM companies WHERE id = %s", (company_id,))
    return cursor.fetchone()


def get_owned_integration(cursor, integration_id, company_id):
    cursor.execute(
        """
        SELECT id, company_id, connection_name, environment_name,
               environment_type, integration_type, provider, api_platform,
               api_url, status, registered_at, last_heartbeat,
               last_status_change, created_at, updated_at
        FROM security_integrations
        WHERE id = %s AND company_id = %s
        """,
        (integration_id, company_id),
    )
    return cursor.fetchone()


def create_integration(request, current_user, integration_type, provider=None, api_platform=None, api_url=None):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        cursor = connection.cursor()
        ensure_integrations_table(cursor)
        company_id = current_user["company_id"]
        company = get_company(cursor, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found.")

        token = f"CYPHERIS-{integration_type}_" + secrets.token_hex(24).upper()
        now = datetime.utcnow()
        cursor.execute(
            """
            INSERT INTO security_integrations
                (company_id, connection_name, environment_name, environment_type,
                 integration_type, provider, api_platform, api_url,
                 enrollment_token, status, registered_at, last_heartbeat,
                 last_status_change, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', NULL, NULL, %s, %s, %s)
            RETURNING id, company_id, connection_name, environment_name,
                      environment_type, integration_type, provider, api_platform,
                      api_url, status, registered_at, last_heartbeat,
                      last_status_change, created_at, updated_at
            """,
            (
                company_id,
                request.connection_name.strip(),
                request.environment_name.strip(),
                request.environment_type.strip() or "infrastructure",
                integration_type,
                provider,
                api_platform,
                str(api_url) if api_url else None,
                token,
                now,
                now,
                now,
            ),
        )
        integration = cursor.fetchone()
        connection.commit()
        return {
            "success": True,
            "message": f"{integration_type.title()} connection created successfully.",
            "company": dict(company),
            "integration": dict(integration),
            "enrollment_token": token,
        }
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to create integration.") from error
    finally:
        connection.close()


@router.post("/cloud")
def create_cloud_integration(request: CloudIntegrationRequest, current_user: dict = Depends(get_current_user)):
    provider = request.provider.strip().lower()
    if provider not in {"aws", "azure", "gcp"}:
        raise HTTPException(status_code=400, detail="Unsupported cloud provider.")
    return create_integration(request, current_user, "CLOUD", provider=provider)


@router.post("/api")
def create_api_integration(request: APIIntegrationRequest, current_user: dict = Depends(get_current_user)):
    platform = request.api_platform.strip().lower()
    if platform not in {"siem", "edr", "custom"}:
        raise HTTPException(status_code=400, detail="Unsupported security API platform.")
    return create_integration(request, current_user, "API", api_platform=platform, api_url=request.api_url)


@router.get("/company")
def get_company_integrations(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor = connection.cursor()
        ensure_integrations_table(cursor)
        cursor.execute(
            """
            SELECT id, company_id, connection_name, environment_name,
                   environment_type, integration_type, provider, api_platform,
                   api_url, status, registered_at, last_heartbeat,
                   last_status_change, created_at, updated_at
            FROM security_integrations
            WHERE company_id = %s
            ORDER BY created_at DESC
            """,
            (current_user["company_id"],),
        )
        return {"success": True, "company_id": current_user["company_id"], "integrations": cursor.fetchall()}
    finally:
        connection.close()


@router.get("/{integration_id}/status")
def get_integration_status(integration_id: int, current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor = connection.cursor()
        ensure_integrations_table(cursor)
        integration = get_owned_integration(cursor, integration_id, current_user["company_id"])
        if not integration:
            raise HTTPException(status_code=404, detail="Security integration not found.")
        return {"success": True, "integration": dict(integration)}
    finally:
        connection.close()


@router.post("/register")
def register_integration(enrollment_token: str):
    """Agent endpoint: the enrollment token acts as the device credential."""
    return _set_agent_status(enrollment_token, "REGISTERED", heartbeat=False)


@router.post("/heartbeat")
def integration_heartbeat(enrollment_token: str):
    """Agent endpoint: the enrollment token acts as the device credential."""
    return _set_agent_status(enrollment_token, "ONLINE", heartbeat=True)


def _set_agent_status(enrollment_token: str, status: str, heartbeat: bool):
    if not enrollment_token or len(enrollment_token) > 255:
        raise HTTPException(status_code=400, detail="Invalid integration credential.")

    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor = connection.cursor()
        ensure_integrations_table(cursor)
        cursor.execute("SELECT id, status FROM security_integrations WHERE enrollment_token = %s", (enrollment_token,))
        integration = cursor.fetchone()
        if not integration:
            raise HTTPException(status_code=404, detail="Invalid integration credential.")

        now = datetime.utcnow()
        changed = integration["status"] != status
        if heartbeat:
            cursor.execute(
                """
                UPDATE security_integrations
                SET status = %s, registered_at = COALESCE(registered_at, %s),
                    last_heartbeat = %s,
                    last_status_change = CASE WHEN %s THEN %s ELSE last_status_change END,
                    updated_at = %s
                WHERE id = %s
                RETURNING id, company_id, connection_name, environment_name,
                          environment_type, integration_type, provider, api_platform,
                          api_url, status, registered_at, last_heartbeat,
                          last_status_change, created_at, updated_at
                """,
                (status, now, now, changed, now, now, integration["id"]),
            )
        else:
            cursor.execute(
                """
                UPDATE security_integrations
                SET status = %s, registered_at = COALESCE(registered_at, %s),
                    last_status_change = CASE WHEN %s THEN %s ELSE last_status_change END,
                    updated_at = %s
                WHERE id = %s
                RETURNING id, company_id, connection_name, environment_name,
                          environment_type, integration_type, provider, api_platform,
                          api_url, status, registered_at, last_heartbeat,
                          last_status_change, created_at, updated_at
                """,
                (status, now, changed, now, now, integration["id"]),
            )
        updated = cursor.fetchone()
        connection.commit()
        return {"success": True, "message": f"Integration status updated to {status}.", "integration": dict(updated)}
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Unable to update integration status.") from error
    finally:
        connection.close()
