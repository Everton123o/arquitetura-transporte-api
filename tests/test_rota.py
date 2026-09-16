from app.normalizadores.rota import RotaStrategy


def dados_rota():
    return {
        "trip_id": "ROT-2026-001",
        "origem": {
            "cidade": "Maceió",
            "uf": "AL",
        },
        "destino": {
            "cidade": "Recife",
            "uf": "PE",
        },
        "partida_em": "2026-10-15T07:00:00-03:00",
        "chegada_em": "2026-10-15T13:00:00-03:00",
        "duracao_minutos": 360,
        "tarifa_centavos": 15000,
        "moeda": "BRL",
        "classe": "semileito",
        "vagas": 12,
    }


def test_reconhece_rota():
    strategy = RotaStrategy()

    dados = dados_rota()

    assert strategy.reconhece(dados) is True


def test_normaliza_viagem_rota():
    strategy = RotaStrategy()

    viagem = strategy.normalizar(dados_rota())

    assert viagem.id_viagem == "ROT-2026-001"
    assert viagem.empresa == "Rota Transportes"

    assert viagem.origem.cidade == "Maceió"
    assert viagem.origem.uf == "AL"

    assert viagem.destino.cidade == "Recife"
    assert viagem.destino.uf == "PE"

    assert viagem.partida == "2026-10-15T07:00:00-03:00"
    assert viagem.chegada == "2026-10-15T13:00:00-03:00"

    assert viagem.duracao_minutos == 360

    assert viagem.preco.valor == 150.00
    assert viagem.preco.moeda == "BRL"

    assert viagem.categoria == "semileito"
    assert viagem.assentos_disponiveis == 12