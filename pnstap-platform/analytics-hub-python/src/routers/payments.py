import hashlib
import hmac
import json
import os
import time

import requests
from fastapi import APIRouter, Depends, HTTPException, Request

from auth import get_current_user
from database import get_db_connection
from routers.billing import PLANS

router = APIRouter(prefix="/api/billing", tags=["Payments"])


@router.post("/checkout")
def create_checkout(current_user: dict = Depends(get_current_user)):
    """Create a Stripe-hosted yearly subscription checkout when Stripe is configured."""
    secret = os.getenv("STRIPE_SECRET_KEY")
    if not secret:
        raise HTTPException(status_code=503, detail="Stripe payments are not configured for this environment.")

    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT plan, annual_price FROM subscriptions WHERE company_id = %s", (current_user["company_id"],))
            subscription = cursor.fetchone()
            if not subscription or subscription["plan"] not in PLANS or subscription["plan"] == "Free":
                raise HTTPException(status_code=400, detail="Select a paid plan before starting checkout.")

            plan = subscription["plan"]
            amount = int(round(float(subscription["annual_price"]) * 100))
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
            payload = {
                "mode": "subscription",
                "success_url": f"{frontend_url}/workspace/billing?payment=success",
                "cancel_url": f"{frontend_url}/workspace/billing?payment=cancelled",
                "client_reference_id": str(current_user["company_id"]),
                "line_items[0][price_data][currency]": "usd",
                "line_items[0][price_data][unit_amount]": str(amount),
                "line_items[0][price_data][recurring][interval]": "year",
                "line_items[0][price_data][product_data][name]": f"Cypheris {plan}",
                "line_items[0][quantity]": "1",
                "metadata[company_id]": str(current_user["company_id"]),
                "metadata[plan]": plan,
            }
            response = requests.post(
                "https://api.stripe.com/v1/checkout/sessions",
                data=payload,
                auth=(secret, ""),
                timeout=20,
            )
            if response.status_code >= 400:
                raise HTTPException(status_code=502, detail="Payment provider rejected the checkout request.")
            session = response.json()
            return {"success": True, "checkout_url": session.get("url"), "session_id": session.get("id")}
    finally:
        connection.close()


def _verify_stripe_signature(payload: bytes, signature: str, secret: str) -> bool:
    timestamp = None
    signatures = []
    for part in signature.split(","):
        key, _, value = part.partition("=")
        if key == "t":
            timestamp = value
        elif key == "v1":
            signatures.append(value)
    if not timestamp or not signatures:
        return False
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False
    except ValueError:
        return False
    signed = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, candidate) for candidate in signatures)


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="Stripe webhook verification is not configured.")
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    if not _verify_stripe_signature(payload, signature, secret):
        raise HTTPException(status_code=400, detail="Invalid Stripe signature.")

    event = json.loads(payload.decode("utf-8"))
    event_type = event.get("type")
    session = event.get("data", {}).get("object", {})
    if event_type == "checkout.session.completed":
        metadata = session.get("metadata", {})
        company_id = metadata.get("company_id")
        plan = metadata.get("plan")
        if company_id and plan in PLANS and plan != "Free":
            connection = get_db_connection()
            if connection is None:
                raise HTTPException(status_code=503, detail="Database connection unavailable.")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE subscriptions
                        SET status = 'ACTIVE', paid_started_at = COALESCE(paid_started_at, CURRENT_TIMESTAMP),
                            payment_provider = 'stripe', external_customer_id = %s,
                            external_subscription_id = %s, renewal_date = CURRENT_DATE + INTERVAL '1 year'
                        WHERE company_id = %s
                        """,
                        (session.get("customer"), session.get("subscription"), int(company_id)),
                    )
                    cursor.execute("UPDATE companies SET status = 'Active', subscription_plan = %s WHERE id = %s", (plan, int(company_id)))
                    connection.commit()
            finally:
                connection.close()
    return {"received": True}
