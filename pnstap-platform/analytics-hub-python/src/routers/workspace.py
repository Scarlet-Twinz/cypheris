from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from database import get_db_connection

router = APIRouter(prefix="/api/workspace", tags=["Workspace"])


class BrandingUpdate(BaseModel):
    logo_url: str | None = Field(default=None, max_length=1000)
    primary_color: str = Field(default="#00E5FF", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field(default="#0A1628", pattern=r"^#[0-9A-Fa-f]{6}$")


@router.get("/company")
def get_company(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, company_name, industry, country, email, phone, website, logo_url, brand_primary_color, brand_secondary_color, subscription_plan, status, created_at, updated_at FROM companies WHERE id = %s",
                (current_user["company_id"],),
            )
            company = cursor.fetchone()
            if not company:
                raise HTTPException(status_code=404, detail="Company not found.")
            return {"success": True, "company": company}
    finally:
        connection.close()


@router.put("/company/branding")
def update_branding(data: BrandingUpdate, current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE companies
                SET logo_url = %s, brand_primary_color = %s, brand_secondary_color = %s
                WHERE id = %s
                RETURNING id, company_name, logo_url, brand_primary_color, brand_secondary_color
                """,
                (data.logo_url, data.primary_color, data.secondary_color, current_user["company_id"]),
            )
            company = cursor.fetchone()
            if not company:
                raise HTTPException(status_code=404, detail="Company not found.")
            connection.commit()
            return {"success": True, "company": company}
    except HTTPException:
        connection.rollback()
        raise
    finally:
        connection.close()


@router.get("/team")
def get_team(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, full_name, email, role, status, last_login, created_at FROM users WHERE company_id = %s ORDER BY created_at ASC",
                (current_user["company_id"],),
            )
            return {"success": True, "members": cursor.fetchall()}
    finally:
        connection.close()


@router.get("/audit")
def get_audit(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, user_id, action, ip_address, metadata, created_at FROM audit_logs WHERE company_id = %s ORDER BY created_at DESC LIMIT 100",
                (current_user["company_id"],),
            )
            return {"success": True, "events": cursor.fetchall()}
    finally:
        connection.close()


@router.get("/integrations")
def integrations_alias(current_user: dict = Depends(get_current_user)):
    """Stable workspace alias for the integration collection."""
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, company_id, connection_name, environment_name, environment_type, integration_type, provider, api_platform, api_url, status, registered_at, last_heartbeat, last_status_change, created_at, updated_at FROM security_integrations WHERE company_id = %s ORDER BY created_at DESC",
                (current_user["company_id"],),
            )
            return {"success": True, "company_id": current_user["company_id"], "integrations": cursor.fetchall()}
    finally:
        connection.close()
