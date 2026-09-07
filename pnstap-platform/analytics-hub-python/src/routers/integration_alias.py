from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from database import get_db_connection

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])


@router.get("")
def list_integrations(current_user: dict = Depends(get_current_user)):
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
