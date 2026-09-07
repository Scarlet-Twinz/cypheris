import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_db_connection
from schemas import UserSignUpRequest, UserLoginRequest
from auth import hash_password, verify_password, create_access_token
from routers.sensors import router as sensors_router
from routers.dashboard import router as dashboard_router
from routers.lyromi import router as lyromi_router
from routers.integrations import router as integrations_router
from routers.integration_alias import router as integration_alias_router
from routers.billing import router as billing_router
from routers.workspace import router as workspace_router

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)


def configured_origins():
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]


app = FastAPI(
    title="Cypheris Security Platform API",
    version="1.0.0",
    description="Security intelligence and infrastructure visibility powered by PNSTAP™.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(lyromi_router)
app.include_router(sensors_router)
app.include_router(integrations_router)
app.include_router(integration_alias_router)
app.include_router(billing_router)
app.include_router(workspace_router)


@app.get("/")
def root():
    return {"application": "Cypheris", "engine": "PNSTAP™", "version": app.version, "status": "online"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/database")
def database_status():
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok")
            cursor.fetchone()
        return {"database": "online"}
    finally:
        connection.close()


@app.post("/auth/signup")
def signup(user: UserSignUpRequest):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (str(user.email).lower(),))
            if cursor.fetchone():
                raise HTTPException(status_code=409, detail="An account with this email already exists.")

            cursor.execute(
                """
                INSERT INTO companies (company_name, industry, country, email, phone, website)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (user.company_name, user.industry, user.country, str(user.email).lower(), user.phone_number, user.website),
            )
            company_id = cursor.fetchone()["id"]

            cursor.execute(
                """
                INSERT INTO users (company_id, full_name, email, phone_number, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, 'Admin')
                RETURNING id, full_name, email, role
                """,
                (company_id, user.full_name, str(user.email).lower(), user.phone_number, hash_password(user.password)),
            )
            admin = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO subscriptions (
                    company_id, plan, billing_cycle, user_limit, current_users,
                    annual_price, trial_started_at, trial_ends_at, status
                )
                VALUES (%s, 'Free', 'Yearly', 1, 1, 0, CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP + INTERVAL '7 days', 'TRIALING')
                """,
                (company_id,),
            )
            connection.commit()

        token = create_access_token({"user_id": admin["id"], "company_id": company_id, "role": admin["role"]})
        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "trial": {"days": 7, "status": "TRIALING"},
            "company": {"id": company_id, "name": user.company_name},
            "administrator": {"id": admin["id"], "name": admin["full_name"], "email": admin["email"], "role": admin["role"]},
        }
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        print("SIGNUP ERROR:", repr(error))
        raise HTTPException(status_code=500, detail="Unable to create the Cypheris workspace.") from error
    finally:
        connection.close()


@app.post("/auth/login")
def login(user: UserLoginRequest):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT users.id, users.company_id, users.full_name, users.email,
                       users.password_hash, users.role, companies.company_name
                FROM users JOIN companies ON users.company_id = companies.id
                WHERE LOWER(users.email) = LOWER(%s) AND users.status = 'Active'
                """,
                (str(user.email),),
            )
            account = cursor.fetchone()
            if account is None or not verify_password(user.password, account["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password.")

            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s", (account["id"],))
            connection.commit()

        token = create_access_token({"user_id": account["id"], "company_id": account["company_id"], "role": account["role"]})
        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": account["id"], "name": account["full_name"], "email": account["email"], "role": account["role"]},
            "company": {"id": account["company_id"], "name": account["company_name"]},
        }
    except HTTPException:
        connection.rollback()
        raise
    except Exception as error:
        connection.rollback()
        print("LOGIN ERROR:", repr(error))
        raise HTTPException(status_code=500, detail="Unable to complete login.") from error
    finally:
        connection.close()
