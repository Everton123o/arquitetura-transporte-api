from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.viagem import ViagemNormalizada, Local, Preco
from app.normalizadores.base import NormalizadorStrategy


class RotaStrategy(NormalizadorStrategy):

    def reconhece(self, dados: dict) -> bool:
        campos = {
            "trip_id",
            "origem",
            "destino",
            "partida_em",
            "chegada_em",
            "duracao_minutos",
            "tarifa_centavos",
            "moeda",
            "classe",
            "vagas",
        }

        return campos.issubset(dados.keys())

    def normalizar(self, dados: dict) -> ViagemNormalizada:
        partida = self._converter_data(
            dados["partida_em"]
        )

        chegada = self._converter_data(
            dados["chegada_em"]
        )

        duracao = self._converter_duracao(
            dados["duracao_minutos"]
        )

        preco = self._converter_preco(
            dados["tarifa_centavos"],
            dados["moeda"],
        )

        categoria = self._normalizar_categoria(
            dados["classe"]
        )

        self._validar_viagem(
            partida,
            chegada,
            duracao,
            preco,
            dados["vagas"],
            dados["origem"],
            dados["destino"],
        )

        return ViagemNormalizada(
            id_viagem=str(dados["trip_id"]),
            empresa="Rota Transportes",
            origem=Local(
                cidade=dados["origem"]["cidade"],
                uf=dados["origem"]["uf"],
            ),
            destino=Local(
                cidade=dados["destino"]["cidade"],
                uf=dados["destino"]["uf"],
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao,
            preco=preco,
            categoria=categoria,
            assentos_disponiveis=int(dados["vagas"]),
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

    def _converter_preco(
        self,
        valor_centavos,
        moeda: str,
    ) -> Preco:

        valor_centavos = int(valor_centavos)

        if valor_centavos <= 0:
            raise ValueError(
                "O preço da passagem deve ser maior que zero."
            )

        if not moeda:
            raise ValueError(
                "A moeda da passagem é obrigatória."
            )

        valor = valor_centavos / 100

        return Preco(
            valor=valor,
            moeda=moeda,
        )

    def _normalizar_categoria(self, valor: str) -> str:
        categorias = {
            "convencional": "convencional",
            "executivo": "executivo",
            "semi-leito": "semileito",
            "semileito": "semileito",
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
        vagas,
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

        if vagas < 0:
            raise ValueError(
                "A quantidade de assentos não pode ser negativa."
            )

        if len(origem["uf"]) != 2:
            raise ValueError(
                "A UF de origem deve possuir exatamente 2 caracteres."
            )

        if len(destino["uf"]) != 2:
            raise ValueError(
                "A UF de destino deve possuir exatamente 2 caracteres."
            )