from app.normalizadores.progresso import ProgressoStrategy


def dados_progresso():
    return {
        "codigoViagem": "PRG-2026-001",
        "cidadeOrigem": "Paulo Afonso",
        "ufOrigem": "BA",
        "cidadeDestino": "Recife",
        "ufDestino": "PE",
        "dataHoraSaida": "2026-10-15T06:30:00-03:00",
        "dataHoraChegada": "2026-10-15T12:50:00-03:00",
        "fusoHorario": "America/Bahia",
        "tempoEstimado": 380,
        "valorPassagem": 129.90,
        "tipoServico": "executivo",
        "assentosDisponiveis": 18,
    }


def test_reconhece_progresso():
    strategy = ProgressoStrategy()

    dados = dados_progresso()

    assert strategy.reconhece(dados) is True


def test_normaliza_viagem_progresso():
    strategy = ProgressoStrategy()

    viagem = strategy.normalizar(dados_progresso())

    assert viagem.id_viagem == "PRG-2026-001"
    assert viagem.empresa == "Auto Viação Progresso"

    assert viagem.origem.cidade == "Paulo Afonso"
    assert viagem.origem.uf == "BA"

    assert viagem.destino.cidade == "Recife"
    assert viagem.destino.uf == "PE"

    assert viagem.partida == "2026-10-15T06:30:00-03:00"
    assert viagem.chegada == "2026-10-15T12:50:00-03:00"

    assert viagem.duracao_minutos == 380

    assert viagem.preco.valor == 129.90
    assert viagem.preco.moeda == "BRL"

    assert viagem.categoria == "executivo"
    assert viagem.assentos_disponiveis == 18