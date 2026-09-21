import os
import requests
from django.db import connections


CPJ_GATEWAY_URL = os.getenv("CPJ_GATEWAY_URL")


def executar_cpj(query, parametros=None):

    parametros = parametros or []

    # Railway → Gateway
    if CPJ_GATEWAY_URL:

        resposta = requests.post(
            f"{CPJ_GATEWAY_URL}/consulta",
            json={
                "query": query,
                "parametros": parametros
            },
            timeout=60
        )

        resposta.raise_for_status()

        dados = resposta.json()

        return dados["colunas"], dados["resultados"]

    # Local → MySQL direto
    with connections["cpj"].cursor() as cursor:

        cursor.execute(query, parametros)

        colunas = [
            coluna[0]
            for coluna in cursor.description
        ]

        resultados = cursor.fetchall()

    return colunas, resultados


def testar_gateway():

    resposta = requests.get(
        f"{CPJ_GATEWAY_URL}/teste-cpj",
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.json()


def consultar_usuarios():

    query = """
        SELECT COUNT(*)
        FROM usuario
    """

    colunas, resultados = executar_cpj(query)

    return resultados[0][0]


def consultar_concluidos(data_inicio, data_fim, evento):

    query = """
        SELECT
            LTRIM(RTRIM(p.numero_processo)) AS numero_processo,
            t.evento AS evento,
            ev.descricao AS nome_evento,
            gp.descricao AS grupo,
            s.descricao AS situacao,
            u.nome AS concluido_por,
            t.cumprido_em AS concluido_em,
            t.texto AS texto

        FROM tramitacao t

        LEFT JOIN cad_processo p
            ON p.pj = t.id_processo

        LEFT JOIN tramitacao_situacao s
            ON s.id_tramitacao_situacao = t.id_tramitacao_situacao

        LEFT JOIN tab_evento ev
            ON ev.sigla = t.evento

        LEFT JOIN tab_grupo_trabalho gp
            ON gp.codigo = p.grupo_trabalho

        LEFT JOIN usuario u
            ON u.id_usuario = t.cumprido_por

        WHERE t.cumprido_em >= %s

        AND t.cumprido_em < DATE_ADD(%s, INTERVAL 1 DAY)

        AND t.evento = %s

        ORDER BY t.cumprido_em DESC
    """

    return executar_cpj(
        query,
        [data_inicio, data_fim, evento]
    )