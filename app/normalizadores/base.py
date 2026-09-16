from abc import ABC, abstractmethod

from app.models.viagem import ViagemNormalizada


class NormalizadorStrategy(ABC):

    @property
    @abstractmethod
    def nome_empresa(self) -> str:
        pass

    @abstractmethod
    def reconhece(self, dados: dict) -> bool:
        pass

    @abstractmethod
    def normalizar(self, dados: dict) -> ViagemNormalizada:
        pass