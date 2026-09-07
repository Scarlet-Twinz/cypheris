from pathlib import Path

from dotenv import load_dotenv

# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    BASE_DIR / ".env",
    override=True
)

# ============================================================
# FASTAPI
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_db_connection

from schemas import (
    UserSignUpRequest,
    UserLoginRequest,
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
)

from routers.sensors import router as sensors_router
from routers.dashboard import router as dashboard_router
from routers.lyromi import router as lyromi_router
from routers.integrations import router as integrations_router


print(
    "========== LOADING CYPHERIS MAIN.PY =========="
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Cypheris Enterprise Security Platform API",
    version="1.0.0",
    description="Powered by PNSTAP™",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    dashboard_router
)

app.include_router(
    lyromi_router
)

app.include_router(
    sensors_router
)

app.include_router(
    integrations_router
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "application": "Cypheris",
        "engine": "PNSTAP™",
        "version": "1.0.0",
        "status": "online",
        "message": (
            "Welcome to Cypheris "
            "Enterprise Security Platform"
        ),
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# DATABASE STATUS
# ============================================================

@app.get("/database")
def database_status():

    conn = get_db_connection()

    if conn is None:
        return {
            "database": "offline"
        }

    try:
        return {
            "database": "online"
        }

    finally:
        conn.close()


# ============================================================
# SIGN UP
# ============================================================

@app.post("/auth/signup")
def signup(user: UserSignUpRequest):

    conn = get_db_connection()

    if conn is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    cur = None

    try:
        cur = conn.cursor()

        # ----------------------------------------------------
        # CHECK EXISTING EMAIL
        # ----------------------------------------------------

        cur.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s;
            """,
            (str(user.email),),
        )

        existing_user = cur.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists.",
            )

        # ----------------------------------------------------
        # CREATE COMPANY
        # ----------------------------------------------------

        cur.execute(
            """
            INSERT INTO companies (
                company_name,
                industry,
                country,
                email,
                phone,
                website
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id;
            """,
            (
                user.company_name,
                user.industry,
                user.country,
                str(user.email),
                user.phone_number,
                user.website,
            ),
        )

        company = cur.fetchone()

        if not company:
            raise HTTPException(
                status_code=500,
                detail="Unable to create company.",
            )

        company_id = company["id"]

        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        password_hash = hash_password(
            user.password
        )

        # ----------------------------------------------------
        # CREATE ADMINISTRATOR
        # ----------------------------------------------------

        cur.execute(
            """
            INSERT INTO users (
                company_id,
                full_name,
                email,
                phone_number,
                password_hash,
                role
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING
                id,
                full_name,
                email,
                role;
            """,
            (
                company_id,
                user.full_name,
                str(user.email),
                user.phone_number,
                password_hash,
                "Admin",
            ),
        )

        admin = cur.fetchone()

        if not admin:
            raise HTTPException(
                status_code=500,
                detail="Unable to create administrator.",
            )

        # ----------------------------------------------------
        # CREATE FREE SUBSCRIPTION
        # ----------------------------------------------------

        cur.execute(
            """
            INSERT INTO subscriptions (
                company_id
            )
            VALUES (%s);
            """,
            (company_id,),
        )

        # ----------------------------------------------------
        # COMMIT EVERYTHING
        # ----------------------------------------------------

        conn.commit()

        # ----------------------------------------------------
        # CREATE TOKEN
        # ----------------------------------------------------

        token = create_access_token(
            {
                "user_id": admin["id"],
                "company_id": company_id,
                "role": admin["role"],
            }
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "status": "success",
            "message": (
                "Welcome to Cypheris "
                "Enterprise Security Platform."
            ),
            "access_token": token,
            "token_type": "bearer",

            "company": {
                "id": company_id,
                "name": user.company_name,
            },

            "administrator": {
                "id": admin["id"],
                "name": admin["full_name"],
                "email": admin["email"],
                "role": admin["role"],
            },
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as error:
        conn.rollback()

        print(
            "SIGNUP ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create the Cypheris workspace.",
        )

    finally:

        if cur:
            cur.close()

        conn.close()


# ============================================================
# LOGIN
# ============================================================

@app.post("/auth/login")
def login(user: UserLoginRequest):

    conn = get_db_connection()

    if conn is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed.",
        )

    cur = None

    try:

        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                users.id,
                users.company_id,
                users.full_name,
                users.email,
                users.password_hash,
                users.role,
                companies.company_name
            FROM users
            INNER JOIN companies
                ON users.company_id = companies.id
            WHERE users.email = %s;
            """,
            (str(user.email),),
        )

        account = cur.fetchone()

        if account is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password.",
            )

        if not verify_password(
            user.password,
            account["password_hash"],
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password.",
            )

        token = create_access_token(
            {
                "user_id": account["id"],
                "company_id": account["company_id"],
                "role": account["role"],
            }
        )

        return {
            "status": "success",
            "message": "Login successful.",
            "access_token": token,
            "token_type": "bearer",

            "user": {
                "id": account["id"],
                "name": account["full_name"],
                "email": account["email"],
                "role": account["role"],
            },

            "company": {
                "id": account["company_id"],
                "name": account["company_name"],
            },
        }

    except HTTPException:
        raise

    except Exception as error:

        print(
            "LOGIN ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to complete login.",
        )

    finally:

        if cur:
            cur.close()

        conn.close()