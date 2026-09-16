from datetime import datetime
from zoneinfo import ZoneInfo

from app.exceptions import ErroNormalizacao
from app.models.viagem import Local, Preco, ViagemNormalizada
from app.normalizadores.base import NormalizadorStrategy


class GontijoStrategy(NormalizadorStrategy):

    @property
    def nome_empresa(self) -> str:
        return "Gontijo"

    def reconhece(self, dados: dict) -> bool:
        campos = {
        "serviceCode",
        "from",
        "to",
        "departure",
        "arrival",
        "estimatedDurationSeconds",
        "fare",
        "serviceClass",
        "availableSeats",
    }

        encontrados = campos.intersection(dados.keys())

        return len(encontrados) >= 2

        return bool(campos_caracteristicos.intersection(dados.keys()))

    def _campo_obrigatorio(self, dados: dict, campo: str):
        if campo not in dados:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                campo,
                f"O campo obrigatório '{campo}' não foi informado.",
            )

    def _campo_nested(self, dados: dict, objeto: str, campo: str):
        if objeto not in dados:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                objeto,
                f"O campo obrigatório '{objeto}' não foi informado.",
            )

        if not isinstance(dados[objeto], dict):
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                objeto,
                f"O campo '{objeto}' deve ser um objeto.",
            )

        if campo not in dados[objeto]:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                f"{objeto}.{campo}",
                f"O campo obrigatório '{objeto}.{campo}' não foi informado.",
            )

    def _data(self, valor, campo: str) -> datetime:
        if not isinstance(valor, str):
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                campo,
                "A data deve estar em formato ISO 8601.",
            )

        try:
            data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        except ValueError as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                campo,
                "A data não pôde ser convertida.",
            ) from erro

        if data.tzinfo is None:
            data = data.replace(tzinfo=ZoneInfo("America/Bahia"))

        return data.astimezone(ZoneInfo("America/Bahia"))

    def normalizar(self, dados: dict) -> ViagemNormalizada:
        campos_obrigatorios = [
            "serviceCode",
            "from",
            "to",
            "departure",
            "arrival",
            "estimatedDurationSeconds",
            "fare",
            "serviceClass",
            "availableSeats",
        ]

        for campo in campos_obrigatorios:
            self._campo_obrigatorio(dados, campo)

        self._campo_nested(dados, "from", "city")
        self._campo_nested(dados, "from", "state")
        self._campo_nested(dados, "to", "city")
        self._campo_nested(dados, "to", "state")
        self._campo_nested(dados, "fare", "amount")
        self._campo_nested(dados, "fare", "currency")

        if len(str(dados["from"]["state"])) != 2:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "from.state",
                "A UF de origem deve possuir exatamente dois caracteres.",
            )

        if len(str(dados["to"]["state"])) != 2:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "to.state",
                "A UF de destino deve possuir exatamente dois caracteres.",
            )

        partida = self._data(dados["departure"], "departure")
        chegada = self._data(dados["arrival"], "arrival")

        if chegada <= partida:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "arrival",
                "A data de chegada deve ser posterior à data de saída.",
            )

        try:
            duracao_segundos = int(dados["estimatedDurationSeconds"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "estimatedDurationSeconds",
                "A duração da viagem deve ser um número inteiro.",
            ) from erro

        if duracao_segundos <= 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "estimatedDurationSeconds",
                "A duração da viagem deve ser maior que zero.",
            )

        if duracao_segundos % 60 != 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "estimatedDurationSeconds",
                "A duração deve resultar em minutos inteiros.",
            )

        duracao = duracao_segundos // 60
        duracao_real = int((chegada - partida).total_seconds() / 60)

        if duracao_real != duracao:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "estimatedDurationSeconds",
                "A duração informada é incompatível com os horários.",
            )

        try:
            valor = float(dados["fare"]["amount"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "fare.amount",
                "O preço da passagem não pôde ser convertido.",
            ) from erro

        if valor <= 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "fare.amount",
                "O preço da passagem deve ser maior que zero.",
            )

        try:
            assentos = int(dados["availableSeats"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "availableSeats",
                "A quantidade de assentos deve ser um número inteiro.",
            ) from erro

        if assentos < 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "availableSeats",
                "A quantidade de assentos não pode ser negativa.",
            )

        categorias = {
            "convencional": "convencional",
            "executivo": "executivo",
            "semileito": "semileito",
            "semi-leito": "semileito",
            "leito": "leito",
        }

        categoria_original = str(dados["serviceClass"]).strip().lower()
        categoria = categorias.get(categoria_original)

        if categoria is None:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "serviceClass",
                "A categoria informada não pôde ser normalizada.",
            )

        return ViagemNormalizada(
            id_viagem=str(dados["serviceCode"]),
            empresa=self.nome_empresa,
            origem=Local(
                cidade=str(dados["from"]["city"]),
                uf=str(dados["from"]["state"]),
            ),
            destino=Local(
                cidade=str(dados["to"]["city"]),
                uf=str(dados["to"]["state"]),
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao,
            preco=Preco(
                valor=valor,
                moeda=str(dados["fare"]["currency"]),
            ),
            categoria=categoria,
            assentos_disponiveis=assentos,
        )