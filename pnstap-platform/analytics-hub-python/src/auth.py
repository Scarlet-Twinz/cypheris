from datetime import datetime, timedelta, timezone
from typing import Optional
import os

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext


load_dotenv()


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ============================================================
# JWT CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is missing from the environment."
    )


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a user's password before storing it.
    """

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a user's password during login.
    """

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# JWT
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate a JWT access token.
    """

    to_encode = data.copy()

    if expires_delta is None:
        expires_delta = timedelta(hours=1)

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({
        "exp": expire,
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )