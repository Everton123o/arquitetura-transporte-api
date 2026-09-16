from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.dependencies import criar_normalizacao_service
from app.exceptions import ErroNormalizacao


router = APIRouter(
    prefix="/api/v1/viagens",
    tags=["Viagens"],
)

normalizacao_service = criar_normalizacao_service()


@router.post("/normalizar")
def normalizar_viagens(viagens: list[dict]):
    try:
        resultado = normalizacao_service.normalizar(viagens)

        return {
            "total": len(resultado),
            "viagens": resultado,
        }

    except ErroNormalizacao as erro:
        return JSONResponse(
            status_code=422,
            content={
                "detail": {
                    "indice": erro.indice,
                    "empresa_identificada": erro.empresa_identificada,
                    "campo": erro.campo,
                    "mensagem": erro.mensagem,
                }
            },
        )