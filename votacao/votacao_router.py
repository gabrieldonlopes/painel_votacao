from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi.templating import Jinja2Templates

from database import get_db
from auth.dependencies import get_current_active_user
from models import User,Chapa,Voto
from schemas import ChapaCreate,VotoCreate
from .votacao_handler import cadastrar_chapa,votar_chapa

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Página de cadastro de chapa
@router.get("/cadastrar-chapa", response_class=HTMLResponse)
async def cadastrar_chapa_page(request: Request, error: str = None, message: str = None):
    return templates.TemplateResponse(
        "cadastrar_chapa.html", 
        {
            "request": request, 
            "error_message": error,
            "success_message": message
        }
    )

@router.post("/cadastrar-chapa", response_class=HTMLResponse)
async def cadastrar_chapa_action(
    request: Request,
    chapa_nome: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Garante que só usuário autenticado acesse
):
    try:
        # Cria objeto de schema
        nova_chapa = ChapaCreate(chapa_nome=chapa_nome)
        
        # Chama a função que faz a lógica de cadastro
        await cadastrar_chapa(nova_chapa, current_user, db)

        # Redireciona para a mesma página com mensagem de sucesso
        return RedirectResponse(
            url=f"/eleicao/cadastrar-chapa?message=Chapa%20cadastrada%20com%20sucesso",
            status_code=303
        )

    except HTTPException as e:
        # Redireciona com mensagem de erro
        return RedirectResponse(
            url=f"/eleicao/cadastrar-chapa?error={e.detail}",
            status_code=303
        )

# Página de votação
@router.get("/votar", response_class=HTMLResponse)
async def votar_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    error: str = None,
    message: str = None
):
    # Carrega as chapas para exibir no select
    result = await db.execute(select(Chapa))
    chapas = result.scalars().all()

    return templates.TemplateResponse(
        "votar.html",
        {
            "request": request,
            "chapas": chapas,
            "error_message": error,
            "success_message": message
        }
    )


@router.post("/votar", response_class=HTMLResponse)
async def votar_action(
    request: Request,
    matricula: str = Form(...),
    chapa_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        novo_voto = VotoCreate(matricula=matricula, chapa_id=chapa_id)
        await votar_chapa(novo_voto, current_user, db)

        return RedirectResponse(
            url=f"/eleicao/votar?message=Voto%20registrado%20com%20sucesso",
            status_code=303
        )

    except HTTPException as e:
        return RedirectResponse(
            url=f"/eleicao/votar?error={e.detail}",
            status_code=303
        )

@router.get("/resultados", response_class=HTMLResponse)
async def resultados_page(request: Request, db: AsyncSession = Depends(get_db)):
    # Conta total de votos
    total_votos_result = await db.execute(select(func.count(Voto.matricula)))
    total_votos = total_votos_result.scalar() or 0

    # Busca votos agrupados por chapa
    votos_por_chapa_result = await db.execute(
        select(Chapa.chapa_nome, func.count(Voto.matricula))
        .join(Voto, Voto.chapa_id == Chapa.chapa_id)
        .group_by(Chapa.chapa_id)
    )
    votos_por_chapa = votos_por_chapa_result.all()

    resultados = []
    for chapa_nome, votos in votos_por_chapa:
        percentual = (votos / total_votos * 100) if total_votos > 0 else 0
        resultados.append({
            "chapa_nome": chapa_nome,
            "total_votos": votos,
            "percentual": round(percentual, 2)
        })

    return templates.TemplateResponse(
        "resultados.html",
        {
            "request": request,
            "total_votos": total_votos,
            "resultados": resultados
        }
    )
