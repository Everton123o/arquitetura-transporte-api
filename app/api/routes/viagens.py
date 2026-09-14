from fastapi import APIRouter

from app.dependencies import criar_normalizacao_service


router = APIRouter(
    prefix="/api/v1/viagens",
    tags=["Viagens"],
)


normalizacao_service = criar_normalizacao_service()


@router.post("/normalizar")
def normalizar_viagens(
    viagens: list[dict],
):
    resultado = normalizacao_service.normalizar(
        viagens
    )

    return {
        "total": len(resultado),
        "viagens": resultado,
    }