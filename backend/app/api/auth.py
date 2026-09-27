from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
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
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        parent, token = await service.login(payload.email, payload.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=token, parent=ParentRead.model_validate(parent))


@router.get("/me", response_model=ParentRead)
async def me(parent: ParentAccount = Depends(get_current_parent)) -> ParentRead:
    return ParentRead.model_validate(parent)
