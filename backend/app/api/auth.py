from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
from app.core.login_guard import login_guard
from app.core.register_guard import register_guard
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


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    # Reaching this point means the body passed validation (a 422 is answered
    # before the handler runs, so malformed requests never spend an attempt).
    ip = _client_ip(request)
    retry_after = register_guard.retry_after(ip)
    if retry_after:
        raise HTTPException(
            status_code=429,
            detail="Too many registration attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )
    # count the attempt BEFORE the DB work, so 201, 409 and even a crash all
    # use it up - otherwise 409 would let anyone probe which emails exist
    register_guard.record_attempt(ip)

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
    ip = _client_ip(request)

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
