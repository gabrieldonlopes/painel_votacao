from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_303_SEE_OTHER

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

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Página de login
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# POST do login via formulário
@router.post("/login", response_class=HTMLResponse)
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = await authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Usuário ou senha inválidos."}
        )

    # Cria token JWT e salva no cookie
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response = RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


# Rota API para registro (para usar no Insomnia/Postman)
@router.post("/register", response_model=UserResponse)
async def register_api(user: UserCreate, db: Session = Depends(get_db)):
    # Verifica se já existe
    db_user = await get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já registrado.")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao criar usuário.")

    return db_user
