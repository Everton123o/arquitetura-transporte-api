from app.normalizadores.progresso import ProgressoStrategy
from app.normalizadores.rota import RotaStrategy
from app.normalizadores.gontijo import GontijoStrategy
from app.normalizadores.sertao_bus import SertaoBusStrategy

from app.registry.normalizadores import NormalizadorRegistry
from app.services.normalizacao import NormalizacaoService


def criar_normalizacao_service() -> NormalizacaoService:
    registry = NormalizadorRegistry()

    registry.registrar(ProgressoStrategy())
    registry.registrar(RotaStrategy())
    registry.registrar(GontijoStrategy())
    registry.registrar(SertaoBusStrategy())

    return NormalizacaoService(registry)