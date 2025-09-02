import uvicorn
import argparse
import asyncio

from fastapi import FastAPI, Request 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database import create_tables
from auth.auth_routes import router as auth_router
from votacao.votacao_router import router as votacao_router
import os
from dotenv import load_dotenv

app = FastAPI()

async def initialize_db(create_db: bool): # verifica se a db existe
    if create_db:
        await create_tables()

PORT = int(os.getenv("PORT"))
HOST = os.getenv("HOST")

app.include_router(auth_router, prefix="/auth")
app.include_router(votacao_router, prefix="/eleicao")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-server",
        action="store_true",
        help="Inicia o servidor Uvicorn."
    )
    parser.add_argument(
        "--create-db",
        action="store_true",
        help="Cria o banco de dados e as tabelas necessárias."
    )
    args = parser.parse_args()

    if args.create_db:
        asyncio.run(initialize_db(args.create_db))

    if args.run_server:
        uvicorn.run("main:app", host=HOST, port=PORT, log_level="info")
    