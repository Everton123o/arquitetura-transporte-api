from abc import ABC, abstractmethod

from app.models.viagem import ViagemNormalizada


class NormalizadorStrategy(ABC):

    @abstractmethod
    def reconhece(self, dados: dict) -> bool:
        pass

    @abstractmethod
    def normalizar(self, dados: dict) -> ViagemNormalizada:
        pass