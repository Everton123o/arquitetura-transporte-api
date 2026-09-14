from app.models.viagem import ViagemNormalizada
from app.registry.normalizadores import NormalizadorRegistry


class NormalizacaoService:

    def __init__(
        self,
        registry: NormalizadorRegistry,
    ):
        self.registry = registry

    def normalizar(
        self,
        viagens: list[dict],
    ) -> list[ViagemNormalizada]:

        resultado = []

        for indice, dados in enumerate(viagens):
            estrategia = self.registry.encontrar(dados)

            if estrategia is None:
                raise ValueError(
                    f"Formato não suportado no índice {indice}."
                )

            viagem = estrategia.normalizar(dados)

            resultado.append(viagem)

        return resultado