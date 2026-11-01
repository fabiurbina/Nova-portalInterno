import os
import requests
from django.db import connections

CPJ_GATEWAY_URL = os.getenv("CPJ_GATEWAY_URL", "").rstrip("/")
CPJ_TIMEOUT = (5, 120)


def executar_cpj(query, parametros=None):
    parametros = parametros or []

    if CPJ_GATEWAY_URL:
        resposta = requests.post(
            f"{CPJ_GATEWAY_URL}/consulta",
            json={
                "query": query,
                "parametros": parametros,
            },
            timeout=CPJ_TIMEOUT,
        )

        if resposta.status_code == 403:
            print("ERRO 403 GATEWAY:", resposta.text)

        resposta.raise_for_status()
        dados = resposta.json()

        if dados.get("status") == "erro":
            raise RuntimeError(
                dados.get(
                    "mensagem",
                    "Erro retornado pelo Gateway CPJ."
                )
            )

        return dados["colunas"], dados["resultados"]

    with connections["cpj"].cursor() as cursor:
        cursor.execute(query, parametros)

        colunas = [
            coluna[0]
            for coluna in cursor.description
        ]

        resultados = cursor.fetchall()

    return colunas, resultados


def _resultados_em_dicts(query, parametros=None):
    colunas, resultados = executar_cpj(
        query,
        parametros
    )

    return [
        dict(zip(colunas, linha))
        for linha in resultados
    ]


def consultar_eventos_rpa_hoje():

    query = """
        SELECT
            COUNT(*) AS qtd,
            s.descricao AS situacao,
            t.evento AS evento,
            UPPER(ev.descricao) AS nome_evento,
            t.cumprido_por AS codigo_robo,

            CASE
                WHEN t.cumprido_por = 831
                    THEN 'Robô Protocolo'

                WHEN t.cumprido_por = 846
                    THEN 'Robô de Guias'

                ELSE 'Não identificado'
            END AS robo

        FROM tramitacao t

        LEFT JOIN tramitacao_situacao s
            ON s.id_tramitacao_situacao =
               t.id_tramitacao_situacao

        INNER JOIN tab_evento ev
            ON ev.sigla = t.evento

        WHERE t.cumprido_por IN (831, 846)

          AND t.cumprido_em >= CURRENT_DATE()

          AND t.cumprido_em <
              CURRENT_DATE() + INTERVAL 1 DAY

        GROUP BY
            s.descricao,
            t.evento,
            ev.descricao,
            t.cumprido_por

        ORDER BY qtd DESC
    """

    return _resultados_em_dicts(query)


def consultar_ultimo_cumprimento_robos():

    query = """
        SELECT
            t.cumprido_por AS codigo_robo,

            CASE
                WHEN t.cumprido_por = 831 THEN 'Robô Protocolo'
                WHEN t.cumprido_por = 846 THEN 'Robô de Guias'
                WHEN t.cumprido_por = 872 THEN 'Robô 872'
            END AS robo,

            MAX(t.cumprido_em) AS ultimo_cumprido_em

        FROM tramitacao t

        WHERE t.cumprido_por IN (831, 846, 872)
          AND t.cumprido_em IS NOT NULL

        GROUP BY t.cumprido_por
    """

    return _resultados_em_dicts(query)


def consultar_media_diaria_robos():

    query = """
        SELECT
            t.cumprido_por AS codigo_robo,

            ROUND(
                COUNT(*) /
                NULLIF(
                    COUNT(
                        DISTINCT DATE(t.cumprido_em)
                    ),
                    0
                ),
                0
            ) AS media_diaria

        FROM tramitacao t

        WHERE t.cumprido_por IN (831, 846, 872)

          AND t.cumprido_em >=
              CURRENT_DATE - INTERVAL 30 DAY

          AND t.cumprido_em < CURRENT_DATE

        GROUP BY t.cumprido_por
    """

    return _resultados_em_dicts(query)