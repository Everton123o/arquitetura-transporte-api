import pytest

from app.exceptions import ErroNormalizacao
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


def verificar_erro(strategy, dados, campo):
    with pytest.raises(ErroNormalizacao) as resultado:
        strategy.normalizar(dados)

    assert resultado.value.campo == campo


def test_campo_obrigatorio_ausente():
    strategy = ProgressoStrategy()
    dados = dados_progresso()

    del dados["cidadeOrigem"]

    verificar_erro(strategy, dados, "cidadeOrigem")


def test_chegada_deve_ser_posterior_a_saida():
    strategy = ProgressoStrategy()
    dados = dados_progresso()

    dados["dataHoraChegada"] = "2026-10-15T05:00:00-03:00"

    with pytest.raises(ErroNormalizacao) as resultado:
        strategy.normalizar(dados)

    assert resultado.value.campo == "dataHoraChegada"
    assert "posterior" in resultado.value.mensagem


def test_duracao_incompativel_com_horarios():
    strategy = ProgressoStrategy()
    dados = dados_progresso()

    dados["tempoEstimado"] = 300

    verificar_erro(strategy, dados, "tempoEstimado")


def test_duracao_nao_pode_ser_zero():
    strategy = ProgressoStrategy()
    dados = dados_progresso()

    dados["tempoEstimado"] = 0

    verificar_erro(strategy, dados, "tempoEstimado")


def test_preco_nao_pode_ser_zero():
    strategy = ProgressoStrategy()
    dados = dados_progresso()

    dados["valorPassagem"] = 0

    verificar_erro(strategy, dados, "valorPassagem")


def test_assentos_nao_podem_ser_negativos():
    strategy = ProgressoStrategy()
    dados = dados_progresso()

    dados["assentosDisponiveis"] = -1

    verificar_erro(strategy, dados, "assentosDisponiveis")


def test_uf_deve_ter_dois_caracteres():
    strategy = ProgressoStrategy()
    dados = dados_progresso()

    dados["ufOrigem"] = "BRA"

    verificar_erro(strategy, dados, "ufOrigem")


def test_categoria_invalida():
    strategy = ProgressoStrategy()
    dados = dados_progresso()

    dados["tipoServico"] = "premium-plus"

    verificar_erro(strategy, dados, "tipoServico")


def test_formato_desconhecido():
    from app.dependencies import criar_normalizacao_service

    service = criar_normalizacao_service()

    dados = [
        {
            "nome": "Formato desconhecido"
        }
    ]

    with pytest.raises(ErroNormalizacao) as resultado:
        service.normalizar(dados)

    assert resultado.value.indice == 0
    assert resultado.value.empresa_identificada is None
    assert resultado.value.campo is None
    assert (
        resultado.value.mensagem
        == "O formato do payload não corresponde a nenhuma companhia suportada."
    )