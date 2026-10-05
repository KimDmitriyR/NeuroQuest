from datetime import datetime, timezone

from app.core.legal import CURRENT_TERMS_VERSION
from app.core.security import create_access_token, hash_password, verify_password
from app.models.parent_account import ParentAccount
from app.repositories.parent_repository import ParentRepository


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, parent_repo: ParentRepository):
        self.parent_repo = parent_repo

    async def register(self, email: str, password: str) -> tuple[ParentAccount, str]:
        # accept_terms=True is already enforced by RegisterRequest's
        # validator before this is ever called - this service only records
        # the fact and moment of consent, it doesn't re-check the flag.
        existing = await self.parent_repo.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(email)

        parent = await self.parent_repo.create(
            email,
            hash_password(password),
            terms_accepted_at=datetime.now(timezone.utc),
            terms_version=CURRENT_TERMS_VERSION,
        )
        token = create_access_token(parent.id)
        return parent, token

    async def login(self, email: str, password: str) -> tuple[ParentAccount, str]:
        parent = await self.parent_repo.get_by_email(email)
        if parent is None or not verify_password(password, parent.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(parent.id)
        return parent, token
