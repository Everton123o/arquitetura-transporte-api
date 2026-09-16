from app.normalizadores.gontijo import GontijoStrategy


def dados_gontijo():
    return {
        "serviceCode": "GON-2026-001",
        "from": {
            "city": "Salvador",
            "state": "BA",
        },
        "to": {
            "city": "Recife",
            "state": "PE",
        },
        "departure": "2026-10-15T08:00:00-03:00",
        "arrival": "2026-10-15T14:30:00-03:00",
        "estimatedDurationSeconds": 23400,
        "fare": {
            "amount": 180.00,
            "currency": "BRL",
        },
        "serviceClass": "LEITO",
        "availableSeats": 20,
    }


def test_reconhece_gontijo():
    strategy = GontijoStrategy()

    dados = dados_gontijo()

    assert strategy.reconhece(dados) is True


def test_normaliza_viagem_gontijo():
    strategy = GontijoStrategy()

    viagem = strategy.normalizar(dados_gontijo())

    assert viagem.id_viagem == "GON-2026-001"
    assert viagem.empresa == "Gontijo"

    assert viagem.origem.cidade == "Salvador"
    assert viagem.origem.uf == "BA"

    assert viagem.destino.cidade == "Recife"
    assert viagem.destino.uf == "PE"

    assert viagem.partida == "2026-10-15T08:00:00-03:00"
    assert viagem.chegada == "2026-10-15T14:30:00-03:00"

    assert viagem.duracao_minutos == 390

    assert viagem.preco.valor == 180.00
    assert viagem.preco.moeda == "BRL"

    assert viagem.categoria == "leito"
    assert viagem.assentos_disponiveis == 20