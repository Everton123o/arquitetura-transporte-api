from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.viagem import ViagemNormalizada, Local, Preco
from app.normalizadores.base import NormalizadorStrategy


class ProgressoStrategy(NormalizadorStrategy):

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

        return campos.issubset(dados.keys())

    def normalizar(self, dados: dict) -> ViagemNormalizada:
        partida = self._converter_data(
            dados["dataHoraSaida"]
        )

        chegada = self._converter_data(
            dados["dataHoraChegada"]
        )

        duracao = self._converter_duracao(
            dados["tempoEstimado"]
        )

        preco = self._converter_preco(
            dados["valorPassagem"]
        )

        categoria = self._normalizar_categoria(
            dados["tipoServico"]
        )

        self._validar_viagem(
            partida,
            chegada,
            duracao,
            preco,
            dados["assentosDisponiveis"],
            dados["ufOrigem"],
            dados["ufDestino"],
        )

        return ViagemNormalizada(
            id_viagem=str(dados["codigoViagem"]),
            empresa="Auto Viação Progresso",
            origem=Local(
                cidade=dados["cidadeOrigem"],
                uf=dados["ufOrigem"],
            ),
            destino=Local(
                cidade=dados["cidadeDestino"],
                uf=dados["ufDestino"],
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao,
            preco=preco,
            categoria=categoria,
            assentos_disponiveis=int(
                dados["assentosDisponiveis"]
            ),
        )

    def _converter_data(self, valor: str) -> datetime:
        data = datetime.fromisoformat(valor)

        if data.tzinfo is None:
            data = data.replace(
                tzinfo=ZoneInfo("America/Bahia")
            )

        return data

    def _converter_duracao(self, valor) -> int:
        duracao = int(valor)

        if duracao <= 0:
            raise ValueError(
                "A duração da viagem deve ser maior que zero."
            )

        return duracao

    def _converter_preco(self, valor) -> Preco:
        valor = float(valor)

        if valor <= 0:
            raise ValueError(
                "O preço da passagem deve ser maior que zero."
            )

        return Preco(
            valor=valor,
            moeda="BRL",
        )

    def _normalizar_categoria(self, valor: str) -> str:
        categorias = {
            "convencional": "convencional",
            "executivo": "executivo",
            "semileito": "semileito",
            "semi-leito": "semileito",
            "leito": "leito",
        }

        categoria = categorias.get(
            valor.lower().strip()
        )

        if categoria is None:
            raise ValueError(
                "Categoria de serviço inválida."
            )

        return categoria

    def _validar_viagem(
        self,
        partida: datetime,
        chegada: datetime,
        duracao: int,
        preco: Preco,
        assentos,
        uf_origem: str,
        uf_destino: str,
    ):
        if chegada <= partida:
            raise ValueError(
                "A data de chegada deve ser posterior à data de saída."
            )

        duracao_real = (
            chegada - partida
        ).total_seconds() / 60

        if duracao_real != duracao:
            raise ValueError(
                "A duração informada não é compatível com os horários."
            )

        if assentos < 0:
            raise ValueError(
                "A quantidade de assentos não pode ser negativa."
            )

        if len(uf_origem) != 2:
            raise ValueError(
                "A UF deve possuir exatamente 2 caracteres."
            )

        if len(uf_destino) != 2:
            raise ValueError(
                "A UF deve possuir exatamente 2 caracteres."
            )