from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

class TokenSettings(BaseSettings):
    secret_key: str = "super_secret_key"
    algorithm: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')


@lru_cache
def get_token_settings():
    return TokenSettings()


class DBSettings(BaseSettings):
    db_user: str
    db_pass: str
    db_host: str
    db_name: str

    def get_sqlalchemy_db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')


class OAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')


@lru_cache
def get_auth_settings():
    return OAuthSettings()


db_settings = DBSettings()
engine = create_async_engine(db_settings.get_sqlalchemy_db_url())
SessionLocal = async_sessionmaker(autoflush=False, bind=engine)


auth_settings = get_auth_settings()
starlette_config = Config(environ=auth_settings.model_dump())
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)