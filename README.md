# 🗳️ Sistema de Votação Grêmio IFBA

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.25-red.svg)](https://www.sqlalchemy.org/)
[![Status](https://img.shields.io/badge/status-ativo-brightgreen.svg)]()

Sistema de votação eletrônica desenvolvido para as eleições do grêmio estudantil do IFBA, permitindo o cadastro de chapas, registro de votos seguros por matrícula e visualização de resultados em tempo real.

O projeto foi construído para facilitar e modernizar o processo eleitoral escolar, garantindo que cada aluno (através da matrícula) vote apenas uma vez. Utiliza FastAPI com processamento assíncrono e banco de dados SQLite para simplicidade na implantação.

## Funcionalidades

| Item | Descrição |
|------|-----------|
| **Autenticação** | Sistema de login para mesários/administradores |
| **Gestão de Chapas** | Cadastro de novas chapas concorrentes |
| **Urna Eletrônica** | Interface para registro de votos usando matrícula |
| **Validação** | Bloqueio de múltiplos votos para a mesma matrícula |
| **Resultados** | Dashboard em tempo real com percentuais e totais |
| **Exportação** | Geração de relatório detalhado em Excel (.xlsx) |

## Como Executar

### Pré-requisitos
- Python 3.9 ou superior
- Pip (gerenciador de pacotes)

### Passos gerais
```bash
# Clone o repositório
git clone https://github.com/gabrieldonlopes/painel_votacao.git
cd painel_votacao

# (Opcional) Crie e ative um ambiente virtual
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
# Crie um arquivo .env na raiz do projeto com:
echo "HOST=0.0.0.0" > .env
echo "PORT=8000" >> .env
echo "SECRET_KEY=token_gerado" >> .env
echo "ADMIN_PASSWORD=senha_segura" >> .env


# Crie o banco de dados e inicie o servidor
python main.py --create-db --run-server