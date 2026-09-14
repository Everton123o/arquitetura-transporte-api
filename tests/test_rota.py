from app.normalizadores.rota import RotaStrategy


def dados_rota():
    return {
        "trip_id": "RTA-2026-001",
        "origem": {
            "cidade": "Paulo Afonso",
            "uf": "BA",
        },
        "destino": {
            "cidade": "Recife",
            "uf": "PE",
        },
        "partida_em": "2026-10-15T06:30:00-03:00",
        "chegada_em": "2026-10-15T11:40:00-03:00",
        "duracao_minutos": 310,
        "tarifa_centavos": 12990,
        "moeda": "BRL",
        "classe": "executivo",
        "vagas": 18,
    }


def test_reconhece_rota():
    strategy = RotaStrategy()

    dados = dados_rota()

    assert strategy.reconhece(dados) is True


def test_normaliza_viagem_rota():
    strategy = RotaStrategy()

    dados = dados_rota()

    viagem = strategy.normalizar(dados)

    assert viagem.id_viagem == "RTA-2026-001"
    assert viagem.empresa == "Rota Transportes"

    assert viagem.origem.cidade == "Paulo Afonso"
    assert viagem.origem.uf == "BA"

    assert viagem.destino.cidade == "Recife"
    assert viagem.destino.uf == "PE"

    assert viagem.partida == "2026-10-15T06:30:00-03:00"
    assert viagem.chegada == "2026-10-15T11:40:00-03:00"

    assert viagem.duracao_minutos == 310

    assert viagem.preco.valor == 129.90
    assert viagem.preco.moeda == "BRL"

    assert viagem.categoria == "executivo"
    assert viagem.assentos_disponiveis == 18