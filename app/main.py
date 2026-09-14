from fastapi import FastAPI

from app.api.routes.viagens import router as viagens_router


app = FastAPI(
    title="API de Integração de Viagens",
    version="1.0.0",
)


app.include_router(viagens_router)


@app.get("/")
def verificar_api():
    return {
        "mensagem": "API de integração de viagens funcionando."
    }