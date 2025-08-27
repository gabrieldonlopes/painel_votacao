import uvicorn
import argparse
import asyncio

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.staticfiles import StaticFiles

from database import create_tables
from auth.auth_router import router as auth_router

app = FastAPI()

async def initialize_db(create_db: bool): # verifica se a db existe
    if create_db:
        await create_tables()
        
app.include_router(auth_router, prefix="/auth")
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
    