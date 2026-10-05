import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    # must be explicitly True - ticking the box on the registration form.
    # Covers consent to the Terms of Use + Privacy Policy, including the
    # parent's consent as legal representative for any child profile they
    # create (children never register or consent themselves).
    accept_terms: bool

    @field_validator("accept_terms")
    @classmethod
    def must_accept_terms(cls, value: bool) -> bool:
        if not value:
            raise ValueError(
                "Необходимо подтвердить согласие с Пользовательским "
                "соглашением и Политикой обработки персональных данных"
            )
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ParentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    created_at: datetime
    terms_accepted_at: datetime
    terms_version: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    parent: ParentRead
