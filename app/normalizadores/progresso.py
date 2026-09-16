from datetime import datetime
from zoneinfo import ZoneInfo

from app.exceptions import ErroNormalizacao
from app.models.viagem import Local, Preco, ViagemNormalizada
from app.normalizadores.base import NormalizadorStrategy


class ProgressoStrategy(NormalizadorStrategy):

    @property
    def nome_empresa(self) -> str:
        return "Auto Viação Progresso"

    def reconhece(self, dados: dict) -> bool:
        campos = {
            "codigoViagem",
            "cidadeOrigem",
            "ufOrigem",
            "cidadeDestino",
            "ufDestino",
            "dataHoraSaida",
            "dataHoraChegada",
            "fusoHorario",
            "tempoEstimado",
            "valorPassagem",
            "tipoServico",
            "assentosDisponiveis",
        }

        encontrados = campos.intersection(dados.keys())
        return len(encontrados) >= 2

    def _campo_obrigatorio(self, dados: dict, campo: str):
        if campo not in dados:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo=campo,
                mensagem=f"O campo obrigatório '{campo}' não foi informado.",
            )

    def _data(self, valor, campo: str) -> datetime:
        if not isinstance(valor, str):
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo=campo,
                mensagem="A data deve estar em formato ISO 8601.",
            )

        try:
            data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        except ValueError as erro:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo=campo,
                mensagem="A data não pôde ser convertida.",
            ) from erro

        if data.tzinfo is None:
            data = data.replace(tzinfo=ZoneInfo("America/Bahia"))

        return data

    def normalizar(self, dados: dict) -> ViagemNormalizada:
        campos_obrigatorios = [
            "codigoViagem",
            "cidadeOrigem",
            "ufOrigem",
            "cidadeDestino",
            "ufDestino",
            "dataHoraSaida",
            "dataHoraChegada",
            "fusoHorario",
            "tempoEstimado",
            "valorPassagem",
            "tipoServico",
            "assentosDisponiveis",
        ]

        for campo in campos_obrigatorios:
            self._campo_obrigatorio(dados, campo)

        if len(dados["ufOrigem"]) != 2:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "ufOrigem",
                "A UF de origem deve possuir exatamente dois caracteres.",
            )

        if len(dados["ufDestino"]) != 2:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "ufDestino",
                "A UF de destino deve possuir exatamente dois caracteres.",
            )

        partida = self._data(dados["dataHoraSaida"], "dataHoraSaida")
        chegada = self._data(dados["dataHoraChegada"], "dataHoraChegada")

        if chegada <= partida:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "dataHoraChegada",
                "A data de chegada deve ser posterior à data de saída.",
            )

        try:
            duracao = int(dados["tempoEstimado"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "tempoEstimado",
                "A duração da viagem deve ser um número inteiro.",
            ) from erro

        if duracao <= 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "tempoEstimado",
                "A duração da viagem deve ser maior que zero.",
            )

        duracao_real = int((chegada - partida).total_seconds() / 60)

        if duracao_real != duracao:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "tempoEstimado",
                "A duração informada é incompatível com os horários.",
            )

        try:
            valor = float(dados["valorPassagem"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "valorPassagem",
                "O preço da passagem não pôde ser convertido.",
            ) from erro

        if valor <= 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "valorPassagem",
                "O preço da passagem deve ser maior que zero.",
            )

        try:
            assentos = int(dados["assentosDisponiveis"])
        except (TypeError, ValueError) as erro:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "assentosDisponiveis",
                "A quantidade de assentos deve ser um número inteiro.",
            ) from erro

        if assentos < 0:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "assentosDisponiveis",
                "A quantidade de assentos não pode ser negativa.",
            )

        categorias = {
            "convencional": "convencional",
            "executivo": "executivo",
            "semileito": "semileito",
            "semi-leito": "semileito",
            "leito": "leito",
        }

        categoria_original = str(dados["tipoServico"]).strip().lower()
        categoria = categorias.get(categoria_original)

        if categoria is None:
            raise ErroNormalizacao(
                -1,
                self.nome_empresa,
                "tipoServico",
                "A categoria informada não pôde ser normalizada.",
            )

        return ViagemNormalizada(
            id_viagem=str(dados["codigoViagem"]),
            empresa=self.nome_empresa,
            origem=Local(
                cidade=str(dados["cidadeOrigem"]),
                uf=str(dados["ufOrigem"]),
            ),
            destino=Local(
                cidade=str(dados["cidadeDestino"]),
                uf=str(dados["ufDestino"]),
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao,
            preco=Preco(
                valor=valor,
                moeda="BRL",
            ),
            categoria=categoria,
            assentos_disponiveis=assentos,
        )