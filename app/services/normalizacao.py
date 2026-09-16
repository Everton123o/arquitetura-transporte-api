from app.exceptions import ErroNormalizacao
from app.models.viagem import ViagemNormalizada
from app.registry.normalizadores import NormalizadorRegistry


class NormalizacaoService:
    def __init__(self, registry: NormalizadorRegistry):
        self.registry = registry

    def normalizar(self, viagens: list[dict]) -> list[ViagemNormalizada]:
        resultado = []

        for indice, dados in enumerate(viagens):
            estrategia = self.registry.encontrar(dados)

            if estrategia is None:
                raise ErroNormalizacao(
                    indice=indice,
                    empresa_identificada=None,
                    campo=None,
                    mensagem=(
                        "O formato do payload não corresponde "
                        "a nenhuma companhia suportada."
                    ),
                )

            try:
                viagem = estrategia.normalizar(dados)
                resultado.append(viagem)

            except ErroNormalizacao as erro:
                raise ErroNormalizacao(
                    indice=indice,
                    empresa_identificada=erro.empresa_identificada,
                    campo=erro.campo,
                    mensagem=erro.mensagem,
                ) from erro

        return resultado