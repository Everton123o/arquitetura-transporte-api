from datetime import datetime
from zoneinfo import ZoneInfo

from app.exceptions import ErroNormalizacao
from app.models.viagem import ViagemNormalizada, Local, Preco
from app.normalizadores.base import NormalizadorStrategy


class RotaStrategy(NormalizadorStrategy):

    @property
    def nome_empresa(self) -> str:
        return "Rota Transportes"

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

        encontrados = campos.intersection(dados.keys())

        return len(encontrados) >= 2

    def normalizar(self, dados: dict) -> ViagemNormalizada:
        campos_obrigatorios = [
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
        ]

        for campo in campos_obrigatorios:
            if campo not in dados:
                raise ErroNormalizacao(
                    indice=-1,
                    empresa_identificada=self.nome_empresa,
                    campo=campo,
                    mensagem=f"O campo obrigatório '{campo}' não foi informado.",
                )

        origem = dados["origem"]
        destino = dados["destino"]

        if not isinstance(origem, dict):
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="origem",
                mensagem="O campo 'origem' deve ser um objeto.",
            )

        if not isinstance(destino, dict):
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="destino",
                mensagem="O campo 'destino' deve ser um objeto.",
            )

        for campo in ["cidade", "uf"]:
            if campo not in origem:
                raise ErroNormalizacao(
                    indice=-1,
                    empresa_identificada=self.nome_empresa,
                    campo=f"origem.{campo}",
                    mensagem=f"O campo obrigatório 'origem.{campo}' não foi informado.",
                )

            if campo not in destino:
                raise ErroNormalizacao(
                    indice=-1,
                    empresa_identificada=self.nome_empresa,
                    campo=f"destino.{campo}",
                    mensagem=f"O campo obrigatório 'destino.{campo}' não foi informado.",
                )

        if len(origem["uf"]) != 2:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="origem.uf",
                mensagem="A UF de origem deve possuir exatamente 2 caracteres.",
            )

        if len(destino["uf"]) != 2:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="destino.uf",
                mensagem="A UF de destino deve possuir exatamente 2 caracteres.",
            )

        try:
            partida = self._converter_data(dados["partida_em"])
        except Exception:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="partida_em",
                mensagem="A data de saída é inválida.",
            )

        try:
            chegada = self._converter_data(dados["chegada_em"])
        except Exception:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="chegada_em",
                mensagem="A data de chegada é inválida.",
            )

        if chegada <= partida:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="chegada_em",
                mensagem="A data de chegada deve ser posterior à data de saída.",
            )

        try:
            duracao = int(dados["duracao_minutos"])
        except (TypeError, ValueError):
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="duracao_minutos",
                mensagem="A duração deve ser um número inteiro válido.",
            )

        if duracao <= 0:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="duracao_minutos",
                mensagem="A duração deve ser maior que zero.",
            )

        duracao_real = int((chegada - partida).total_seconds() / 60)

        if duracao != duracao_real:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="duracao_minutos",
                mensagem="A duração informada é incompatível com os horários de saída e chegada.",
            )

        try:
            tarifa_centavos = float(dados["tarifa_centavos"])
        except (TypeError, ValueError):
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="tarifa_centavos",
                mensagem="A tarifa deve ser um número válido.",
            )

        if tarifa_centavos <= 0:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="tarifa_centavos",
                mensagem="A tarifa deve ser maior que zero.",
            )

        valor = tarifa_centavos / 100

        try:
            vagas = int(dados["vagas"])
        except (TypeError, ValueError):
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="vagas",
                mensagem="A quantidade de vagas deve ser um número inteiro válido.",
            )

        if vagas < 0:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="vagas",
                mensagem="A quantidade de vagas não pode ser negativa.",
            )

        categoria = self._normalizar_categoria(dados["classe"])

        if categoria is None:
            raise ErroNormalizacao(
                indice=-1,
                empresa_identificada=self.nome_empresa,
                campo="classe",
                mensagem="A categoria informada não pode ser normalizada.",
            )

        moeda = str(dados["moeda"]).upper()

        return ViagemNormalizada(
            id_viagem=str(dados["trip_id"]),
            empresa=self.nome_empresa,
            origem=Local(
                cidade=str(origem["cidade"]),
                uf=str(origem["uf"]).upper(),
            ),
            destino=Local(
                cidade=str(destino["cidade"]),
                uf=str(destino["uf"]).upper(),
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao,
            preco=Preco(
                valor=valor,
                moeda=moeda,
            ),
            categoria=categoria,
            assentos_disponiveis=vagas,
        )

    def _converter_data(self, valor: str) -> datetime:
        data = datetime.fromisoformat(valor)

        if data.tzinfo is None:
            data = data.replace(
                tzinfo=ZoneInfo("America/Bahia")
            )

        return data.astimezone(
            ZoneInfo("America/Bahia")
        )

    def _normalizar_categoria(self, valor: str) -> str | None:
        categoria = str(valor).strip().lower()

        categorias = {
            "convencional": "convencional",
            "convencional executivo": "executivo",
            "executivo": "executivo",
            "semi-leito": "semileito",
            "semileito": "semileito",
            "semi leito": "semileito",
            "leito": "leito",
        }

        return categorias.get(categoria)