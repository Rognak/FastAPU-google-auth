import datetime
import random

from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse

from core.utils import PasswordUtils, TokenUtils
from sqlalchemy.ext.asyncio import AsyncSession
from queries import user as user_queries

from contracts import LoginPasswordSchema, Token, UserSchema
from dependencies import get_db
from core.config import get_token_settings, TokenSettings, oauth


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login_via_password", response_model=Token)
async def login_via_password(login: LoginPasswordSchema,
                db: AsyncSession = Depends(get_db),
                token_settings: TokenSettings = Depends(get_token_settings)
                ):
    user = await user_queries.get_by_email(db=db, email=login.email)

    if user is None or not PasswordUtils.verify_password(login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректное имя пользователя или пароль")

    return Token(
        access_token=TokenUtils.create_access_token({"sub": user.email},
                                                    expires_delta=datetime.timedelta(minutes=1),
                                                    token_settings=token_settings),
        refresh_token=TokenUtils.create_access_token({"sub": user.email},
                                                     expires_delta=datetime.timedelta(minutes=10),
                                                     token_settings=token_settings,
                                                     token_type='refresh'),
        token_type="Bearer")


@router.get('/login_via_google')
async def login_via_google(request: Request):
    redirect_uri = 'http://127.0.0.1:8080/auth/token_google'  # This creates the url for our /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/token_google')
async def auth(request: Request,
               db: AsyncSession = Depends(get_db),
               token_settings: TokenSettings = Depends(get_token_settings)):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user = access_token.get('userinfo')

    # проверяем есть ли пользователь
    app_user = await user_queries.get_by_email(db, user.email)
    if not app_user:
        from random_username.generate import generate_username

        user = UserSchema(
            username=f"{generate_username(1)[0]}",
            email=user.email,
            full_name=user.name
        )

        app_user = await user_queries.create(db=db, user_schema=user)

    token = Token(
        access_token=TokenUtils.create_access_token({"sub": app_user.email},
                                                    expires_delta=datetime.timedelta(minutes=1),
                                                    token_settings=token_settings),
        refresh_token=TokenUtils.create_access_token({"sub": app_user.email},
                                                     expires_delta=datetime.timedelta(minutes=10),
                                                     token_settings=token_settings,
                                                     token_type='refresh'),
        token_type="Bearer")

    request.session["tokens"] = token.model_dump()
    return RedirectResponse('/')

