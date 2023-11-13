from fastapi import FastAPI, Depends
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse

from core.config import TokenSettings, get_token_settings
from dependencies import get_db, get_current_user
from queries.user import get_by_email

from routes import books_router, auth_router, user_router


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret")

app.include_router(books_router)
app.include_router(user_router)
app.include_router(auth_router)


@app.get('/')
async def root(request: Request, db: AsyncSession = Depends(get_db),
               token_settins: TokenSettings = Depends(get_token_settings)):
    tokens = request.session.get("tokens")
    if tokens:
        user = await get_current_user(token=tokens.get("access_token"), db=db, token_settings=token_settins)
        return HTMLResponse('<body>'
                            f'<h1>Hello, {user.full_name}!</h1><br>'
                            '<a href="/auth/login_via_google">Log In</a>'
                            '</body>')

    return HTMLResponse('<body>'
                        '<h1>Hello, anonymous!</h1><br>'
                        '<a href="/auth/login_via_google">Log In</a>'
                        '</body>')


if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, reload=True)
