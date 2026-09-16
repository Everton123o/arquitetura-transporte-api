from datetime import datetime
from zoneinfo import ZoneInfo

from app.exceptions import ErroNormalizacao
from app.models.viagem import Local, Preco, ViagemNormalizada
from app.normalizadores.base import NormalizadorStrategy


class SertaoBusStrategy(NormalizadorStrategy):

    @property
    def nome_empresa(self) -> str:
        return "Sertão Bus"

    def reconhece(self, dados: dict) -> bool:
        campos = {
        "numero",
        "rota",
        "horarios",
        "duracao_horas",
        "preco_total",
        "moeda",
        "servico",
        "lugares_livres",
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

        return data

    def _local(self, valor, campo: str) -> Local:
        if not isinstance(valor, str):
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                campo,
                "O local deve estar no formato 'Cidade/UF'.",
            )

        partes = valor.rsplit("/", 1)

        if len(partes) != 2:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                campo,
                "O local deve estar no formato 'Cidade/UF'.",
            )

        cidade = partes[0].strip()
        uf = partes[1].strip()

        if not cidade:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                campo,
                "A cidade não pode estar vazia.",
            )

        if len(uf) != 2:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                campo,
                "A UF deve possuir exatamente dois caracteres.",
            )

        return Local(
            cidade=cidade,
            uf=uf,
        )

    def normalizar(self, dados: dict) -> ViagemNormalizada:
        campos_obrigatorios = [
            "numero",
            "rota",
            "horarios",
            "duracao_horas",
            "preco_total",
            "moeda",
            "servico",
            "lugares_livres",
        ]

        for campo in campos_obrigatorios:
            self._campo_obrigatorio(dados, campo)

        self._campo_nested(dados, "rota", "partida")
        self._campo_nested(dados, "rota", "chegada")
        self._campo_nested(dados, "horarios", "saida")
        self._campo_nested(dados, "horarios", "chegada")

        origem = self._local(
            dados["rota"]["partida"],
            "rota.partida",
        )

        destino = self._local(
            dados["rota"]["chegada"],
            "rota.chegada",
        )

        partida = self._data(
            dados["horarios"]["saida"],
            "horarios.saida",
        )

        chegada = self._data(
            dados["horarios"]["chegada"],
            "horarios.chegada",
        )

        if chegada <= partida:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "horarios.chegada",
                "A data de chegada deve ser posterior à data de saída.",
            )

        try:
            duracao_horas = float(dados["duracao_horas"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "duracao_horas",
                "A duração da viagem não pôde ser convertida.",
            ) from erro

        if duracao_horas <= 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "duracao_horas",
                "A duração da viagem deve ser maior que zero.",
            )

        duracao_minutos_decimal = duracao_horas * 60

        if not duracao_minutos_decimal.is_integer():
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "duracao_horas",
                "A duração deve resultar em minutos inteiros.",
            )

        duracao = int(duracao_minutos_decimal)

        duracao_real = int((chegada - partida).total_seconds() / 60)

        if duracao_real != duracao:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "duracao_horas",
                "A duração informada é incompatível com os horários.",
            )

        try:
            valor = float(dados["preco_total"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "preco_total",
                "O preço da passagem não pôde ser convertido.",
            ) from erro

        if valor <= 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "preco_total",
                "O preço da passagem deve ser maior que zero.",
            )

        try:
            assentos = int(dados["lugares_livres"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "lugares_livres",
                "A quantidade de assentos deve ser um número inteiro.",
            ) from erro

        if assentos < 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "lugares_livres",
                "A quantidade de assentos não pode ser negativa.",
            )

        categorias = {
            "conv": "convencional",
            "convencional": "convencional",
            "exec": "executivo",
            "executivo": "executivo",
            "semi": "semileito",
            "semileito": "semileito",
            "semi-leito": "semileito",
            "leito": "leito",
        }

        categoria_original = str(dados["servico"]).strip().lower()
        categoria = categorias.get(categoria_original)

        if categoria is None:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "servico",
                "A categoria informada não pôde ser normalizada.",
            )

        return ViagemNormalizada(
            id_viagem=str(dados["numero"]),
            empresa=self.nome_empresa,
            origem=origem,
            destino=destino,
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao,
            preco=Preco(
                valor=valor,
                moeda=str(dados["moeda"]),
            ),
            categoria=categoria,
            assentos_disponiveis=assentos,
        )