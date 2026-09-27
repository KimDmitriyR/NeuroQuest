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
        existing = await self.parent_repo.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(email)

        parent = await self.parent_repo.create(email, hash_password(password))
        token = create_access_token(parent.id)
        return parent, token

    async def login(self, email: str, password: str) -> tuple[ParentAccount, str]:
        parent = await self.parent_repo.get_by_email(email)
        if parent is None or not verify_password(password, parent.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(parent.id)
        return parent, token
