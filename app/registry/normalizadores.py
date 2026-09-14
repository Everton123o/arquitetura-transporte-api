from app.normalizadores.base import NormalizadorStrategy


class NormalizadorRegistry:

    def __init__(self):
        self._estrategias: list[NormalizadorStrategy] = []

    def registrar(self, estrategia: NormalizadorStrategy):
        self._estrategias.append(estrategia)

    def encontrar(
        self,
        dados: dict,
    ) -> NormalizadorStrategy | None:

        for estrategia in self._estrategias:
            if estrategia.reconhece(dados):
                return estrategia

        return None