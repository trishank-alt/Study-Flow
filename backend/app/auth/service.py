from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.repository import AuthRepository
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.schemas import UserCreate, UserLogin, Token, UserResponse
from app.shared.config import get_settings
from app.shared.exceptions import DuplicateError, AuthError


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)
        self.settings = get_settings()

    async def register_user(self, data: UserCreate) -> UserResponse:
        existing = await self.repo.find_by_email(data.email)
        if existing:
            raise DuplicateError("A user with this email already exists")

        hashed = hash_password(data.password)
        user = await self.repo.create_user(data.email, hashed)
        return UserResponse.model_validate(user)

    async def login_user(self, data: UserLogin) -> Token:
        user = await self.repo.find_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise AuthError("Invalid email or password")

        token = create_access_token(
            data={"sub": str(user.id)},
            secret_key=self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM,
            expires_delta=timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=token)
