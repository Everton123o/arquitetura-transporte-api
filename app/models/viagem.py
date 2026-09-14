from pydantic import BaseModel


class Local(BaseModel):
    cidade: str
    uf: str


class Preco(BaseModel):
    valor: float
    moeda: str


class ViagemNormalizada(BaseModel):
    id_viagem: str
    empresa: str
    origem: Local
    destino: Local
    partida: str
    chegada: str
    duracao_minutos: int
    preco: Preco
    categoria: str
    assentos_disponiveis: int