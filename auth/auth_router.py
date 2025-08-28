from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST

from auth.auth_handler import (
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_user,
    get_password_hash,
)
from database import get_db
from models import User
from schemas import UserCreate, UserResponse

from fastapi.templating import Jinja2Templates
from datetime import timedelta
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Página de login
@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request, 
    error: Optional[str] = None,
    message: Optional[str] = None
):
    return templates.TemplateResponse(
        "login.html", 
        {
            "request": request, 
            "error_message": error,
            "success_message": message
        }
    )

# POST do login via formulário
@router.post("/login", response_class=HTMLResponse)
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    user = await authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "error_message": "Usuário ou senha inválidos."
            }
        )

    # Ajusta tempo de expiração baseado no "remember me"
    if remember_me:
        access_token_expires = timedelta(days=7)  # 7 dias se lembrar
    else:
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
        secure=True,  # Adicionado secure para HTTPS (em produção)
        samesite="lax",  # Proteção CSRF
        max_age=access_token_expires.total_seconds() if remember_me else None
    )
    return response


# Logout - limpa o cookie de autenticação
@router.post("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response


# Rota API para registro (apenas para Insomnia/Swagger)
@router.post("/register", response_model=UserResponse)
async def register_api(user: UserCreate, db: Session = Depends(get_db)):
    # Verifica se já existe
    db_user = await get_user(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, 
            detail="Usuário já registrado."
        )

    # Validação de força de senha (opcional)
    if len(user.password) < 6:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="A senha deve ter pelo menos 6 caracteres."
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, 
            detail="Erro ao criar usuário."
        )

    return db_user