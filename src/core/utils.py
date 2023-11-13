from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from core.config import TokenSettings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenUtils:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None,
                            token_settings: TokenSettings = None,
                            token_type: str = "access"
                            ):
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=token_settings.access_token_expire_minutes)

        to_encode.update({"exp": expire, "token_type": token_type})
        encoded_jwt = jwt.encode(to_encode, token_settings.secret_key, algorithm=token_settings.algorithm)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str, token_settings: TokenSettings = None):
        try:
            encoded_jwt = jwt.decode(token, token_settings.secret_key, algorithms=[token_settings.algorithm])
        except jwt.JWSError:
            return None
        return encoded_jwt


class PasswordUtils:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hash: str) -> bool:
        return pwd_context.verify(password, hash)