import pandas as pd
from fastapi import UploadFile

def importar_excel(uploaded_file: UploadFile) -> pd.DataFrame:
    nome_arquivo = uploaded_file.filename.lower()
    dtype = {"CPF": str}  # Força leitura da coluna CPF como string

    if nome_arquivo.endswith(".xls"):
        df = pd.read_excel(uploaded_file.file, engine="xlrd", skiprows=1, dtype=dtype)
    elif nome_arquivo.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file.file, engine="openpyxl", skiprows=1, dtype=dtype)
    else:
        raise ValueError("Formato não suportado: use .xls ou .xlsx")
