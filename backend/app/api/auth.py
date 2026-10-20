from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
from app.core.login_guard import login_guard
from app.models.parent_account import ParentAccount
from app.repositories.parent_repository import ParentRepository
from app.schemas.auth import LoginRequest, ParentRead, RegisterRequest, TokenResponse
from app.services.auth_service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(ParentRepository(db))


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        parent, token = await service.register(payload.email, payload.password)
    except EmailAlreadyRegisteredError:
        raise HTTPException(status_code=409, detail="Email already registered")
    return TokenResponse(access_token=token, parent=ParentRead.model_validate(parent))


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    ip = request.client.host if request.client else "unknown"

    # refuse BEFORE hitting the DB / bcrypt, so a flood stays cheap
    retry_after = login_guard.retry_after(ip, payload.email)
    if retry_after:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    try:
        parent, token = await service.login(payload.email, payload.password)
    except InvalidCredentialsError:
        login_guard.record_failure(ip, payload.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    login_guard.record_success(ip, payload.email)
    return TokenResponse(access_token=token, parent=ParentRead.model_validate(parent))


@router.get("/me", response_model=ParentRead)
async def me(parent: ParentAccount = Depends(get_current_parent)) -> ParentRead:
    return ParentRead.model_validate(parent)
