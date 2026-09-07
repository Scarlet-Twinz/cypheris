import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(
    ENV_FILE,
    override=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    try:
        host = os.getenv(
            "DB_HOST",
            "127.0.0.1"
        )

        port = os.getenv(
            "DB_PORT",
            "5432"
        )

        database = os.getenv(
            "DB_NAME",
            "pnstap"
        )

        user = os.getenv(
            "DB_USER",
            "postgres"
        )

        password = os.getenv(
            "DB_PASSWORD"
        )

        if not password:
            print(
                "DATABASE CONNECTION ERROR: "
                "DB_PASSWORD is missing."
            )
            return None

        print(
            "DATABASE CONFIG:",
            f"host={host}",
            f"port={port}",
            f"database={database}",
            f"user={user}",
        )

        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            cursor_factory=RealDictCursor,
        )

        print(
            "DATABASE CONNECTION: SUCCESS"
        )

        return connection

    except Exception as error:
        print(
            "DATABASE CONNECTION ERROR:",
            repr(error)
        )
        raise