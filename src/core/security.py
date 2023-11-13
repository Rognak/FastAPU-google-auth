from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from dependencies import get_db
from abc import ABC, abstractmethod
from queries.user import get_by_email
from core.utils import PasswordUtils, TokenUtils
from fastapi.security import HTTPBearer
from core.config import TokenSettings, get_token_settings


class AbstractJWTAuth(ABC):

    @staticmethod
    @abstractmethod
    def authenticate_user(*args, **kwargs):
        pass


class PasswordJWTAuth(AbstractJWTAuth):

    @staticmethod
    def authenticate_user(email, password, db: AsyncSession = Depends(get_db)):
        user = get_by_email(db=db, email=email)
        if not user:
            return False
        if not PasswordUtils.verify_password(password, user.hashed_password):
            return False
        return user


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, token_settings: TokenSettings = Depends(get_token_settings)):
        credentials = await super(JWTBearer, self).__call__(request)
        exp = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid auth token")
        if credentials:
            token = TokenUtils.decode_access_token(credentials.credentials, token_settings)
            if token is None:
                raise exp
            if token.get('token_type') != 'access':
                raise exp

            return credentials.credentials
        else:
            raise exp



