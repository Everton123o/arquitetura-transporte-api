# API de Integração e Homogeneidade de Dados em uma API de Transporte Rodoviário

API desenvolvida em Python com FastAPI para receber dados de viagens de diferentes empresas de transporte, identificar automaticamente o formato recebido e normalizar os dados para um único padrão.

Empresas suportadas:

- Auto Viação Progresso
- Rota Transportes
- Gontijo
- Sertão Bus

## Tecnologias

- Python
- FastAPI
- Pydantic
- Pytest
- Uvicorn

## Instalação

Crie o ambiente virtual:

```powershell
python -m venv .venv

Testes

Para executar os testes:

python -m pytest -q