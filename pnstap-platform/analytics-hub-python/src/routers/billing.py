from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user, require_admin
from database import get_db_connection

router = APIRouter(prefix="/api/billing", tags=["Billing"])

PLANS = {
    "Free": {"annual_price": 0, "user_limit": 1, "retention_days": 7, "ai": "Core"},
    "Pro": {"annual_price": 1000, "user_limit": 5, "retention_days": 30, "ai": "Basic"},
    "Business": {"annual_price": 5000, "user_limit": 50, "retention_days": 90, "ai": "Advanced"},
    "Enterprise": {"annual_price": 15000, "user_limit": 1000000, "retention_days": 365, "ai": "Custom"},
}


class PlanSelection(BaseModel):
    plan: str = Field(..., min_length=2, max_length=30)
    billing_cycle: str = Field(default="Yearly", max_length=20)
    payment_provider: str = Field(default="stripe", max_length=30)


def _subscription_payload(row):
    now = datetime.now(timezone.utc)
    trial_ends = row["trial_ends_at"]
    if trial_ends.tzinfo is None:
        trial_ends = trial_ends.replace(tzinfo=timezone.utc)
    trial_active = row["status"] == "TRIALING" and trial_ends > now
    days_remaining = max(0, (trial_ends - now).days) if trial_active else 0
    plan = row["plan"]
    config = PLANS.get(plan, PLANS["Free"])
    access = row["status"] in {"ACTIVE", "TRIALING"} and (row["status"] == "ACTIVE" or trial_active)
    return {"plan": plan, "billing_cycle": row["billing_cycle"], "annual_price": float(row["annual_price"]), "user_limit": config["user_limit"], "retention_days": config["retention_days"], "ai_tier": config["ai"], "status": "TRIALING" if trial_active else row["status"], "trial_started_at": row["trial_started_at"], "trial_ends_at": trial_ends, "trial_active": trial_active, "trial_days_remaining": days_remaining, "access_granted": access, "payment_provider": row["payment_provider"], "renewal_date": row["renewal_date"]}


@router.get("/plans")
def get_plans():
    return {"trial": {"days": 7, "access": "full platform access"}, "overage": {"price": 10, "unit": "user/month", "applies_to": "users above plan limit"}, "plans": PLANS, "payment_methods": ["Stripe", "PayPal", "Bank transfer (Enterprise)"]}


@router.get("/subscription")
def get_subscription(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if connection is None: raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM subscriptions WHERE company_id = %s", (current_user["company_id"],))
            row = cursor.fetchone()
            if row is None: raise HTTPException(status_code=404, detail="Subscription not found.")
            return {"success": True, "subscription": _subscription_payload(row)}
    finally: connection.close()


@router.post("/select-plan")
def select_plan(selection: PlanSelection, current_user: dict = Depends(require_admin)):
    if selection.plan not in PLANS: raise HTTPException(status_code=400, detail="Unknown Cypheris plan.")
    if selection.billing_cycle.lower() != "yearly": raise HTTPException(status_code=400, detail="Cypheris billing is currently yearly.")
    if selection.payment_provider.lower() not in {"stripe", "paypal", "bank_transfer"}: raise HTTPException(status_code=400, detail="Unsupported payment provider.")
    if selection.plan == "Enterprise" and selection.payment_provider.lower() != "bank_transfer": raise HTTPException(status_code=400, detail="Enterprise direct payment uses bank transfer.")
    config = PLANS[selection.plan]
    connection = get_db_connection()
    if connection is None: raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""UPDATE subscriptions SET plan=%s,billing_cycle=%s,user_limit=%s,annual_price=%s,payment_provider=%s,status=CASE WHEN %s='Free' THEN 'ACTIVE' ELSE 'PENDING_PAYMENT' END,updated_at=CURRENT_TIMESTAMP WHERE company_id=%s RETURNING *""", (selection.plan,selection.billing_cycle,config["user_limit"],config["annual_price"],selection.payment_provider.lower(),selection.plan,current_user["company_id"]))
            row = cursor.fetchone()
            if row is None: raise HTTPException(status_code=404, detail="Subscription not found.")
            cursor.execute("UPDATE companies SET subscription_plan=%s,status=%s WHERE id=%s", (selection.plan,"Active" if selection.plan == "Free" else "Payment Required",current_user["company_id"]))
            connection.commit()
            return {"success":True,"message":"Plan selected. Connect the configured payment provider to complete paid activation.","subscription":_subscription_payload(row)}
    except HTTPException:
        connection.rollback(); raise
    finally: connection.close()
