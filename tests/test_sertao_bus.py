from app.normalizadores.sertao_bus import SertaoBusStrategy


def dados_sertao_bus():
    return {
        "numero": "SER-2026-100",
        "rota": {
            "partida": "Paulo Afonso/BA",
            "chegada": "Maceió/AL",
        },
        "horarios": {
            "saida": "2026-10-16T08:00:00-03:00",
            "chegada": "2026-10-16T13:30:00-03:00",
        },
        "duracao_horas": 5.5,
        "preco_total": 105.90,
        "moeda": "BRL",
        "servico": "EXEC",
        "lugares_livres": 14,
    }


def test_reconhece_sertao_bus():
    strategy = SertaoBusStrategy()

    dados = dados_sertao_bus()

    assert strategy.reconhece(dados) is True


def test_normaliza_viagem_sertao_bus():
    strategy = SertaoBusStrategy()

    viagem = strategy.normalizar(dados_sertao_bus())

    assert viagem.id_viagem == "SER-2026-100"
    assert viagem.empresa == "Sertão Bus"

    assert viagem.origem.cidade == "Paulo Afonso"
    assert viagem.origem.uf == "BA"

    assert viagem.destino.cidade == "Maceió"
    assert viagem.destino.uf == "AL"

    assert viagem.partida == "2026-10-16T08:00:00-03:00"
    assert viagem.chegada == "2026-10-16T13:30:00-03:00"

    assert viagem.duracao_minutos == 330

    assert viagem.preco.valor == 105.90
    assert viagem.preco.moeda == "BRL"

    assert viagem.categoria == "executivo"
    assert viagem.assentos_disponiveis == 14