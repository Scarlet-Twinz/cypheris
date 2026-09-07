import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from auth import get_current_user, hash_password, require_admin
from database import get_db_connection

router = APIRouter(prefix="/api/workspace", tags=["Workspace"])


class BrandingUpdate(BaseModel):
    logo_url: str | None = Field(default=None, max_length=1000)
    primary_color: str = Field(default="#00E5FF", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field(default="#0A1628", pattern=r"^#[0-9A-Fa-f]{6}$")


class MemberInvite(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)
    role: str = Field(default="Analyst", pattern=r"^(Admin|Analyst|Viewer)$")


class AcceptInvite(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    password: str = Field(min_length=8, max_length=128)


def _connection_or_503():
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    return connection


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _can_customize(plan: str, status: str) -> bool:
    return status.upper() == "TRIALING" or plan in {"Business", "Enterprise"}


@router.get("/company")
def get_company(current_user: dict = Depends(get_current_user)):
    connection = _connection_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, company_name, industry, country, email, phone, website, timezone, currency, logo_url, brand_primary_color, brand_secondary_color, subscription_plan, status, created_at, updated_at FROM companies WHERE id = %s",
                (current_user["company_id"],),
            )
            company = cursor.fetchone()
            if not company:
                raise HTTPException(status_code=404, detail="Company not found.")
            return {"success": True, "company": company}
    finally:
        connection.close()


@router.put("/company/branding")
def update_branding(data: BrandingUpdate, current_user: dict = Depends(require_admin)):
    connection = _connection_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT subscription_plan, status FROM companies WHERE id = %s", (current_user["company_id"],))
            company_plan = cursor.fetchone()
            if not company_plan:
                raise HTTPException(status_code=404, detail="Company not found.")
            if not _can_customize(company_plan["subscription_plan"], company_plan["status"]):
                raise HTTPException(status_code=403, detail="Custom branding is available during trial and on Business or Enterprise plans.")
            cursor.execute(
                """
                UPDATE companies SET logo_url = %s, brand_primary_color = %s, brand_secondary_color = %s
                WHERE id = %s
                RETURNING id, company_name, logo_url, brand_primary_color, brand_secondary_color
                """,
                (data.logo_url, data.primary_color, data.secondary_color, current_user["company_id"]),
            )
            company = cursor.fetchone()
            connection.commit()
            return {"success": True, "company": company}
    except HTTPException:
        connection.rollback()
        raise
    finally:
        connection.close()


@router.get("/team")
def get_team(current_user: dict = Depends(get_current_user)):
    connection = _connection_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, full_name, email, role, status, last_login, created_at FROM users WHERE company_id = %s ORDER BY created_at ASC",
                (current_user["company_id"],),
            )
            return {"success": True, "members": cursor.fetchall(), "current_role": current_user.get("role")}
    finally:
        connection.close()


@router.get("/invitations")
def get_invitations(current_user: dict = Depends(require_admin)):
    connection = _connection_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, email, full_name, role, expires_at, accepted_at, created_at FROM workspace_invitations WHERE company_id = %s ORDER BY created_at DESC LIMIT 100",
                (current_user["company_id"],),
            )
            return {"success": True, "invitations": cursor.fetchall()}
    finally:
        connection.close()


@router.post("/invitations")
def create_invitation(data: MemberInvite, current_user: dict = Depends(require_admin)):
    connection = _connection_or_503()
    raw_token = secrets.token_urlsafe(32)
    token_hash = _token_hash(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    email = str(data.email).lower()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(%s)", (email,))
            if cursor.fetchone():
                raise HTTPException(status_code=409, detail="A user with that email already exists.")
            cursor.execute("SELECT user_limit, current_users FROM subscriptions WHERE company_id = %s", (current_user["company_id"],))
            subscription = cursor.fetchone()
            if not subscription:
                raise HTTPException(status_code=404, detail="Subscription not found.")
            if subscription["current_users"] >= subscription["user_limit"]:
                raise HTTPException(status_code=403, detail="The current plan has reached its member limit.")
            cursor.execute("SELECT id FROM workspace_invitations WHERE company_id = %s AND LOWER(email) = LOWER(%s) AND accepted_at IS NULL AND expires_at > CURRENT_TIMESTAMP", (current_user["company_id"], email))
            if cursor.fetchone():
                raise HTTPException(status_code=409, detail="An active invitation already exists for that email.")
            cursor.execute(
                """
                INSERT INTO workspace_invitations (company_id, email, full_name, role, token_hash, invited_by, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, email, full_name, role, expires_at, created_at
                """,
                (current_user["company_id"], email, data.full_name.strip(), data.role, token_hash, current_user["user_id"], expires_at),
            )
            invitation = cursor.fetchone()
            connection.commit()
            return {"success": True, "invitation": invitation, "invite_token": raw_token}
    except HTTPException:
        connection.rollback()
        raise
    finally:
        connection.close()


@router.post("/invitations/accept")
def accept_invitation(data: AcceptInvite):
    connection = _connection_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, company_id, email, full_name, role FROM workspace_invitations WHERE token_hash = %s AND accepted_at IS NULL AND expires_at > CURRENT_TIMESTAMP",
                (_token_hash(data.token),),
            )
            invitation = cursor.fetchone()
            if not invitation:
                raise HTTPException(status_code=400, detail="This invitation is invalid or has expired.")
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(%s)", (invitation["email"],))
            if cursor.fetchone():
                raise HTTPException(status_code=409, detail="A user with that email already exists.")
            cursor.execute(
                "INSERT INTO users (company_id, full_name, email, password_hash, role) VALUES (%s, %s, %s, %s, %s) RETURNING id, full_name, email, role, company_id",
                (invitation["company_id"], invitation["full_name"], invitation["email"], hash_password(data.password), invitation["role"]),
            )
            user = cursor.fetchone()
            cursor.execute("UPDATE workspace_invitations SET accepted_at = CURRENT_TIMESTAMP WHERE id = %s", (invitation["id"],))
            cursor.execute("UPDATE subscriptions SET current_users = current_users + 1 WHERE company_id = %s", (invitation["company_id"],))
            cursor.execute("INSERT INTO audit_logs (company_id, user_id, action, metadata) VALUES (%s, %s, 'member.invited.accepted', %s)", (invitation["company_id"], user["id"], '{"source":"workspace_invitation"}'))
            connection.commit()
            return {"success": True, "user": user}
    except HTTPException:
        connection.rollback()
        raise
    finally:
        connection.close()


@router.get("/audit")
def get_audit(current_user: dict = Depends(get_current_user)):
    connection = _connection_or_503()
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
    connection = _connection_or_503()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, company_id, connection_name, environment_name, environment_type, integration_type, provider, api_platform, api_url, status, registered_at, last_heartbeat, last_status_change, created_at, updated_at FROM security_integrations WHERE company_id = %s ORDER BY created_at DESC",
                (current_user["company_id"],),
            )
            return {"success": True, "company_id": current_user["company_id"], "integrations": cursor.fetchall()}
    finally:
        connection.close()
