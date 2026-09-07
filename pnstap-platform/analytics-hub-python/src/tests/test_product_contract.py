import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from routers.billing import PLANS  # noqa: E402
from schemas import UserSignUpRequest  # noqa: E402


def test_cypheris_pricing_contract():
    assert PLANS["Free"]["annual_price"] == 0
    assert PLANS["Pro"]["annual_price"] == 1000
    assert PLANS["Business"]["annual_price"] == 5000
    assert PLANS["Enterprise"]["annual_price"] == 15000
    assert PLANS["Free"]["user_limit"] == 1
    assert PLANS["Pro"]["user_limit"] == 5
    assert PLANS["Business"]["user_limit"] == 50
    assert PLANS["Enterprise"]["user_limit"] >= 1000000


def test_signup_requires_strong_password():
    with pytest.raises(ValueError):
        UserSignUpRequest(
            company_name="Example Security",
            full_name="Admin User",
            email="admin@example.com",
            password="password",
            confirm_password="password",
        )


def test_signup_accepts_valid_password():
    request = UserSignUpRequest(
        company_name="Example Security",
        full_name="Admin User",
        email="admin@example.com",
        password="SecurePass123",
        confirm_password="SecurePass123",
    )
    assert request.email == "admin@example.com"
