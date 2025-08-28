from fastapi import HTTPException,status
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession 

from sqlalchemy import func

from schemas import ChapaCreate,VotoCreate
from models import User,Chapa,Voto

async def cadastrar_chapa(nova_chapa:ChapaCreate,user:User,db:AsyncSession):
    if not user:
        raise HTTPException(status_code=401,detail="Usuário não autorizado")

    chapa_result = await db.execute(select(Chapa).where(func.lower(Chapa.chapa_nome) == nova_chapa.chapa_nome.lower()))
    chapa_obj = chapa_result.scalars().first()

    if chapa_obj:
        raise HTTPException(status_code=409, detail="Chapa já criada")
    
    db_chapa = Chapa(
        chapa_nome=nova_chapa.chapa_nome
    )

    try:
        db.add(db_chapa)
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar chapa. Detalhes: {str(e)}",
        )
    return {"message":"Chapa cadastrada com sucesso"}
    

async def votar_chapa(novo_voto:VotoCreate,user:User,db:AsyncSession):
    if not user:
        raise HTTPException(status_code=401,detail="Usuário não autorizado")
    
    voto_result = await db.execute(select(Voto).where(Voto.matricula == novo_voto.matricula))
    voto_obj = voto_result.scalars().first()

    if voto_obj:
        raise HTTPException(status_code=409, detail="Você já votou!")
    
    chapa_result = await db.execute(select(Chapa).where(Chapa.chapa_id == novo_voto.chapa_id))
    chapa_obj = chapa_result.scalars().first()
    
    if not chapa_obj:
        raise HTTPException(status_code=404, detail="Chapa não existe")


    from datetime import datetime
    db_voto = Voto(
        matricula=novo_voto.matricula,
        horario=datetime.now(),
        chapa_id=novo_voto.chapa_id
    )

    try:
        db.add(db_voto)
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao votar. Detalhes: {str(e)}",
        )
    return {"message":"Voto cadastrado com sucesso"}
    
