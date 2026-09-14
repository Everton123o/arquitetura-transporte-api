from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.viagem import ViagemNormalizada, Local, Preco
from app.normalizadores.base import NormalizadorStrategy


class GontijoStrategy(NormalizadorStrategy):

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

        return campos.issubset(dados.keys())

    def normalizar(self, dados: dict) -> ViagemNormalizada:
        partida = self._converter_data(
            dados["departure"]
        )

        chegada = self._converter_data(
            dados["arrival"]
        )

        duracao = self._converter_duracao(
            dados["estimatedDurationSeconds"]
        )

        preco = self._converter_preco(
            dados["fare"]
        )

        categoria = self._normalizar_categoria(
            dados["serviceClass"]
        )

        self._validar_viagem(
            partida,
            chegada,
            duracao,
            preco,
            dados["availableSeats"],
            dados["from"],
            dados["to"],
        )

        return ViagemNormalizada(
            id_viagem=str(dados["serviceCode"]),
            empresa="Gontijo",
            origem=Local(
                cidade=dados["from"]["city"],
                uf=dados["from"]["state"],
            ),
            destino=Local(
                cidade=dados["to"]["city"],
                uf=dados["to"]["state"],
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao,
            preco=preco,
            categoria=categoria,
            assentos_disponiveis=int(
                dados["availableSeats"]
            ),
        )

    def _converter_data(self, valor: str) -> datetime:
        data = datetime.fromisoformat(
            valor.replace("Z", "+00:00")
        )

        if data.tzinfo is None:
            data = data.replace(
                tzinfo=ZoneInfo("America/Bahia")
            )

        return data.astimezone(
            ZoneInfo("America/Bahia")
        )

    def _converter_duracao(self, valor) -> int:
        segundos = int(valor)

        if segundos <= 0:
            raise ValueError(
                "A duração da viagem deve ser maior que zero."
            )

        minutos = segundos / 60

        if minutos != int(minutos):
            raise ValueError(
                "A duração em segundos deve resultar em minutos inteiros."
            )

        return int(minutos)

    def _converter_preco(self, valor: dict) -> Preco:
        if "amount" not in valor or "currency" not in valor:
            raise ValueError(
                "Os dados da tarifa são inválidos."
            )

        preco = float(valor["amount"])

        if preco <= 0:
            raise ValueError(
                "O preço da passagem deve ser maior que zero."
            )

        return Preco(
            valor=preco,
            moeda=valor["currency"],
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
        origem: dict,
        destino: dict,
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

        if len(origem["state"]) != 2:
            raise ValueError(
                "A UF de origem deve possuir exatamente 2 caracteres."
            )

        if len(destino["state"]) != 2:
            raise ValueError(
                "A UF de destino deve possuir exatamente 2 caracteres."
            )