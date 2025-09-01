# dependencies.py
from typing import Optional
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .auth_handler import decode_access_token
from database import get_db
from models import User
from schemas import TokenData
from .auth_handler import SECRET_KEY  # apenas para referência se necessário
import jwt

async def _get_token_from_request(request: Request) -> Optional[str]:
    """
    Prefer cookie 'access_token'. Como fallback aceita Authorization header.
    Cookie armazenado como 'Bearer <token>'.
    """
    token = None
    cookie = request.cookies.get("access_token")
    if cookie:
        token = cookie.removeprefix("Bearer ").strip()
    else:
        # fallback - header Authorization: Bearer <token>
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
    return token


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    token = await _get_token_from_request(request)
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None

    # Busca usuário no banco
    result = await db.execute(
        select(User).filter(User.username == token_data.username)
    )
    user = result.scalars().first()
    return user

async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    if current_user and not current_user.is_active:
        return None
    return current_user
