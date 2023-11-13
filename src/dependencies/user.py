from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from jose import jwt, JWTError
from core.config import TokenSettings, get_token_settings
from contracts import TokenData
from core.security import JWTBearer
from dependencies import get_db
from queries.user import get_by_email


async def get_current_user(token: Annotated[str, Depends(JWTBearer())],
                           db: AsyncSession = Depends(get_db),
                           token_settings: TokenSettings = Depends(get_token_settings)
                           ):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, token_settings.secret_key, algorithms=[token_settings.algorithm])
        email: str = payload.get("sub")
        token_type: str = payload.get("token_type")

        if email is None:
            raise credentials_exception

        if token_type is None or token_type != 'access':
            raise credentials_exception

        token_data = TokenData(email=email, token_type=token_type)
    except JWTError:
        raise credentials_exception
    user = await get_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
