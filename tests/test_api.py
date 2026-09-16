from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


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


def test_endpoint_normaliza_viagem():
    response = client.post(
        "/api/v1/viagens/normalizar",
        json=[dados_progresso()],
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["total"] == 1
    assert len(dados["viagens"]) == 1

    viagem = dados["viagens"][0]

    assert viagem["id_viagem"] == "PRG-2026-001"
    assert viagem["empresa"] == "Auto Viação Progresso"
    assert viagem["duracao_minutos"] == 380
    assert viagem["categoria"] == "executivo"
    assert viagem["assentos_disponiveis"] == 18


def test_endpoint_normaliza_multiplas_empresas():
    response = client.post(
        "/api/v1/viagens/normalizar",
        json=[
            dados_progresso(),
            dados_rota(),
        ],
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["total"] == 2

    assert dados["viagens"][0]["empresa"] == "Auto Viação Progresso"
    assert dados["viagens"][1]["empresa"] == "Rota Transportes"


def test_endpoint_preserva_ordem_das_viagens():
    progresso = dados_progresso()
    rota = dados_rota()

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=[
            rota,
            progresso,
        ],
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["viagens"][0]["id_viagem"] == "ROT-2026-001"
    assert dados["viagens"][1]["id_viagem"] == "PRG-2026-001"


def test_endpoint_retorna_422_para_formato_desconhecido():
    response = client.post(
        "/api/v1/viagens/normalizar",
        json=[
            {
                "nome": "Formato desconhecido"
            }
        ],
    )

    assert response.status_code == 422

    dados = response.json()

    assert dados["detail"]["indice"] == 0
    assert dados["detail"]["empresa_identificada"] is None
    assert dados["detail"]["campo"] is None
    assert (
        dados["detail"]["mensagem"]
        == "O formato do payload não corresponde a nenhuma companhia suportada."
    )


def test_endpoint_retorna_422_para_campo_obrigatorio_ausente():
    dados = dados_progresso()

    del dados["cidadeOrigem"]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=[dados],
    )

    assert response.status_code == 422

    erro = response.json()["detail"]

    assert erro["indice"] == 0
    assert erro["empresa_identificada"] == "Auto Viação Progresso"
    assert erro["campo"] == "cidadeOrigem"
    assert (
        erro["mensagem"]
        == "O campo obrigatório 'cidadeOrigem' não foi informado."
    )


def test_endpoint_rejeita_lote_inteiro_quando_um_item_e_invalido():
    valido = dados_progresso()

    invalido = dados_rota()
    invalido["chegada_em"] = "2026-10-15T06:00:00-03:00"

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=[
            valido,
            invalido,
        ],
    )

    assert response.status_code == 422

    erro = response.json()["detail"]

    assert erro["indice"] == 1
    assert erro["empresa_identificada"] == "Rota Transportes"
    assert erro["campo"] == "chegada_em"
    assert "posterior" in erro["mensagem"]

    assert "viagens" not in response.json()