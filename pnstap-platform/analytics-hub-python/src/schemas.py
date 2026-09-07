from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserSignUpRequest(BaseModel):
    # ============================================================
    # COMPANY INFORMATION
    # ============================================================

    company_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    industry: Optional[str] = None

    country: Optional[str] = None

    website: Optional[str] = None

    # ============================================================
    # ADMINISTRATOR INFORMATION
    # ============================================================

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone_number: Optional[str] = None

    # ============================================================
    # SECURITY
    # ============================================================

    password: str = Field(
        ...,
        min_length=8,
    )

    confirm_password: str

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> EmailStr:
        # IMPORTANT:
        # Do not call EmailStr(...) here.
        # Pydantic has already validated the email.
        return str(value).strip().lower()

    @field_validator("country", "industry", "website", "phone_number")
    @classmethod
    def normalize_optional_fields(cls, value: Optional[str]):
        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        has_upper = any(character.isupper() for character in value)
        has_lower = any(character.islower() for character in value)
        has_digit = any(character.isdigit() for character in value)

        if not has_upper:
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not has_lower:
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not has_digit:
            raise ValueError(
                "Password must contain at least one number."
            )

        return value

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError(
                "Confirm password is too short."
            )

        return value


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> EmailStr:
        return str(value).strip().lower()