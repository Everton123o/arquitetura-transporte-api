from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.viagem import ViagemNormalizada, Local, Preco
from app.normalizadores.base import NormalizadorStrategy


class SertaoBusStrategy(NormalizadorStrategy):

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

        return campos.issubset(dados.keys())

    def normalizar(self, dados: dict) -> ViagemNormalizada:
        partida = self._converter_data(
            dados["horarios"]["saida"]
        )

        chegada = self._converter_data(
            dados["horarios"]["chegada"]
        )

        duracao = self._converter_duracao(
            dados["duracao_horas"]
        )

        preco = self._converter_preco(
            dados["preco_total"],
            dados["moeda"],
        )

        categoria = self._normalizar_categoria(
            dados["servico"]
        )

        origem = self._converter_local(
            dados["rota"]["partida"]
        )

        destino = self._converter_local(
            dados["rota"]["chegada"]
        )

        self._validar_viagem(
            partida,
            chegada,
            duracao,
            preco,
            dados["lugares_livres"],
            origem,
            destino,
        )

        return ViagemNormalizada(
            id_viagem=str(dados["numero"]),
            empresa="Sertão Bus",
            origem=origem,
            destino=destino,
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao,
            preco=preco,
            categoria=categoria,
            assentos_disponiveis=int(
                dados["lugares_livres"]
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

        return data

    def _converter_duracao(self, valor) -> int:
        horas = float(valor)

        if horas <= 0:
            raise ValueError(
                "A duração da viagem deve ser maior que zero."
            )

        minutos = horas * 60

        if minutos != int(minutos):
            raise ValueError(
                "A duração deve resultar em minutos inteiros."
            )

        return int(minutos)

    def _converter_preco(
        self,
        valor,
        moeda: str,
    ) -> Preco:

        preco = float(valor)

        if preco <= 0:
            raise ValueError(
                "O preço da passagem deve ser maior que zero."
            )

        if not moeda:
            raise ValueError(
                "A moeda da passagem é obrigatória."
            )

        return Preco(
            valor=preco,
            moeda=moeda,
        )

    def _converter_local(self, valor: str) -> Local:
        partes = valor.split("/")

        if len(partes) != 2:
            raise ValueError(
                "O local deve possuir o formato 'Cidade/UF'."
            )

        cidade = partes[0].strip()
        uf = partes[1].strip()

        if not cidade:
            raise ValueError(
                "A cidade é obrigatória."
            )

        if len(uf) != 2:
            raise ValueError(
                "A UF deve possuir exatamente 2 caracteres."
            )

        return Local(
            cidade=cidade,
            uf=uf,
        )

    def _normalizar_categoria(self, valor: str) -> str:
        categorias = {
            "CONV": "convencional",
            "CONVENCIONAL": "convencional",
            "EXEC": "executivo",
            "EXECUTIVO": "executivo",
            "SEMI": "semileito",
            "SEMILEITO": "semileito",
            "SEMI-LEITO": "semileito",
            "LEITO": "leito",
        }

        categoria = categorias.get(
            valor.upper().strip()
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
        origem: Local,
        destino: Local,
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