from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Página de inicial
@router.get("/", response_class=HTMLResponse)
async def votacao_home(request: Request):
    return templates.TemplateResponse("votacao_home.html", {"request": request, "error": None})

@router.get("/cadastro_chapa", response_class=HTMLResponse)
async def votacao_home(request: Request):
    return templates.TemplateResponse("form_cadastro.html", {"request": request, "error": None})

@router.get("/votar_chapa", response_class=HTMLResponse)
async def votacao_home(request: Request):
    return templates.TemplateResponse("form_votar.html", {"request": request, "error": None})


