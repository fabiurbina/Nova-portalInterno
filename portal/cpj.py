from django.db import connections


def consultar_usuarios():

    with connections['cpj'].cursor() as cursor:

        cursor.execute("""
            SELECT COUNT(*)
            FROM usuario
        """)

        resultado = cursor.fetchone()

    return resultado[0]


def consultar_concluidos(data_inicio, data_fim, evento):

    query = """
        SELECT
            LTRIM(RTRIM(p.numero_processo)) AS numero_processo,
            t.evento as evento,
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

    with connections['cpj'].cursor() as cursor:

        cursor.execute(
            query,
            [data_inicio, data_fim, evento]
        )

        colunas = [coluna[0] for coluna in cursor.description]

        resultados = cursor.fetchall()

    return colunas, resultados