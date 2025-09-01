import os
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from sqlalchemy.future import select
from dotenv import load_dotenv

from fastapi.templating import Jinja2Templates
from datetime import timedelta

from .auth_handler import create_access_token, get_password_hash, verify_password
from .dependencies import get_current_user
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, TokenData

templates = Jinja2Templates(directory="templates")
router = APIRouter()

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    result = await db.execute(__import__("sqlalchemy").future.select(User).filter(User.username == username))
    user = result.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

load_dotenv()

# Environment flags
ENV = os.getenv("ENV", "development")
COOKIE_SECURE = True if ENV == "production" else False
COOKIE_SAMESITE = "lax"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None, message: Optional[str] = None):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error_message": error,
            "success_message": message
        }
    )


@router.post("/login", response_class=HTMLResponse)
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    admin_password: str = Form(...),
    remember_me: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    if int(admin_password) != int(ADMIN_PASSWORD):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="tá tentando hackear meu site é?")
    
    user = await authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": "Usuário ou senha inválidos."}
        )

    # Ajusta tempo de expiração
    if remember_me:
        access_token_expires = timedelta(days=3)
    else:
        # padrão definido em auth_handler ACCESS_TOKEN_EXPIRE_MINUTES
        from .auth_handler import ACCESS_TOKEN_EXPIRE_MINUTES
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    response = RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=int(access_token_expires.total_seconds())
    )
    return response


@router.post("/logout", response_class=HTMLResponse)
async def logout_action():
    response = RedirectResponse(url="/auth/login", status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@router.post("/register", response_class=JSONResponse)
async def register_api(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if user.admin_password != int(ADMIN_PASSWORD):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="tá tentando hackear meu site é?")

    # Verifica se já existe
    result = await db.execute(select(User).filter(User.username == user.username))
    db_user = result.scalars().first()
    
    if db_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Usuário já registrado.")

    # Validação mínima de senha
    if len(user.password) < 6:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="A senha deve ter pelo menos 6 caracteres.")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Erro ao criar usuário.")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"message":"registro feito com sucesso"}
