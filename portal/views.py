import logging
import threading

from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from django.contrib.auth.decorators import login_required
from django.db import close_old_connections
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from .models import CacheDashboardRPA

from .cpj import (
    consultar_eventos_rpa_hoje,
    consultar_ultimo_cumprimento_robos,
    consultar_media_diaria_robos,
)


logger = logging.getLogger(__name__)

_lock_sincronizacao_rpa = threading.Lock()

TEMPO_CACHE_MINUTOS = 2

TEMPO_SINCRONIZACAO_EXPIRADA_MINUTOS = 5

TEMPO_ROBO_ATIVO_MINUTOS = 20


def formatar_data_execucao(valor):

    if not valor:
        return "Sem registro"

    if isinstance(valor, str):

        texto = valor.strip()

        try:
            valor = parsedate_to_datetime(texto)

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            valor = parse_datetime(texto)

        if valor is None:
            return f"Data inválida: {texto}"

    if not isinstance(valor, datetime):
        return "Data inválida"

    return valor.strftime(
        "%d/%m/%Y às %H:%M:%S"
    )


def _converter_data(valor):

    if not valor:
        return None

    if isinstance(valor, datetime):

        data = valor

    else:

        texto = str(valor).strip()

        try:

            data = parsedate_to_datetime(texto)

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            data = parse_datetime(texto)

        if data is None:
            return None

    if timezone.is_naive(data):

        data = timezone.make_aware(
            data,
            timezone.get_current_timezone(),
        )

    return timezone.localtime(data)


def _tornar_json_serializavel(valor):

    if isinstance(valor, dict):

        return {
            str(chave): _tornar_json_serializavel(item)

            for chave, item in valor.items()
        }

    if isinstance(valor, (list, tuple)):

        return [
            _tornar_json_serializavel(item)

            for item in valor
        ]

    if isinstance(valor, datetime):

        return valor.isoformat()

    if hasattr(valor, "isoformat"):

        try:

            return valor.isoformat()

        except (
            TypeError,
            ValueError,
        ):

            pass

    return valor


def _sincronizar_dashboard_rpa():

    try:

        close_old_connections()

        eventos = consultar_eventos_rpa_hoje()

        ultimas_atividades = (
            consultar_ultimo_cumprimento_robos()
        )

        medias_robos = consultar_media_diaria_robos()

        dados = {

            "eventos": _tornar_json_serializavel(
                eventos or []
            ),

            "ultimas_atividades": (
                _tornar_json_serializavel(
                    ultimas_atividades or []
                )
            ),

            "medias_robos": (
                _tornar_json_serializavel(
                    medias_robos or []
                )
            ),
        }

        CacheDashboardRPA.objects.update_or_create(

            chave="dashboard_rpa",

            defaults={

                "dados": dados,

                "ultima_atualizacao": timezone.now(),

                "sincronizando": False,

                "inicio_sincronizacao": None,

                "ultimo_erro": "",
            },
        )

    except Exception as erro:

        logger.exception(
            "Erro ao sincronizar o dashboard RPA"
        )

        try:

            CacheDashboardRPA.objects.update_or_create(

                chave="dashboard_rpa",

                defaults={

                    "sincronizando": False,

                    "inicio_sincronizacao": None,

                    "ultimo_erro": str(erro)[:4000],
                },
            )

        except Exception:

            logger.exception(
                "Erro ao registrar falha da sincronização"
            )

    finally:

        close_old_connections()

        if _lock_sincronizacao_rpa.locked():

            try:

                _lock_sincronizacao_rpa.release()

            except RuntimeError:

                logger.exception(
                    "Não foi possível liberar o lock da sincronização"
                )


def _iniciar_sincronizacao_rpa():

    if not _lock_sincronizacao_rpa.acquire(
        blocking=False
    ):

        return False

    try:

        cache, _ = CacheDashboardRPA.objects.get_or_create(

            chave="dashboard_rpa",

            defaults={
                "dados": {}
            },
        )

        if cache.sincronizando:

            inicio = cache.inicio_sincronizacao

            sincronizacao_recente = (

                inicio

                and timezone.now() - inicio

                < timedelta(
                    minutes=(
                        TEMPO_SINCRONIZACAO_EXPIRADA_MINUTOS
                    )
                )
            )

            if sincronizacao_recente:

                _lock_sincronizacao_rpa.release()

                return False

        cache.sincronizando = True

        cache.inicio_sincronizacao = timezone.now()

        cache.ultimo_erro = ""

        cache.save(

            update_fields=[

                "sincronizando",

                "inicio_sincronizacao",

                "ultimo_erro",
            ]
        )

        thread = threading.Thread(

            target=_sincronizar_dashboard_rpa,

            daemon=True,

            name="sincronizacao-dashboard-rpa",
        )

        thread.start()

        return True

    except Exception:

        if _lock_sincronizacao_rpa.locked():

            _lock_sincronizacao_rpa.release()

        raise


@login_required(login_url="login")
def dashboard_rpa(request):

    cache, _ = CacheDashboardRPA.objects.get_or_create(

        chave="dashboard_rpa",

        defaults={
            "dados": {}
        },
    )

    cache_vencido = (

        not cache.ultima_atualizacao

        or timezone.now() - cache.ultima_atualizacao

        > timedelta(
            minutes=TEMPO_CACHE_MINUTOS
        )
    )

    if cache_vencido and not cache.sincronizando:

        try:

            _iniciar_sincronizacao_rpa()

        except Exception:

            logger.exception(
                "Não foi possível iniciar a sincronização do dashboard"
            )

        cache.refresh_from_db()

    dados = cache.dados or {}

    eventos_rpa = dados.get(
        "eventos",
        []
    )

    ultimas_atividades = dados.get(
        "ultimas_atividades",
        []
    )

    medias_robos = dados.get(
        "medias_robos",
        []
    )

    agora = timezone.localtime(
        timezone.now()
    )

    limite_atividade = agora - timedelta(
        minutes=TEMPO_ROBO_ATIVO_MINUTOS
    )

    metas = {

        item["codigo_robo"]: int(
            item.get("media_diaria") or 0
        )

        for item in medias_robos
    }

    robos = {}

    for item in ultimas_atividades:

        codigo = item["codigo_robo"]

        ultimo_original = item.get(
            "ultimo_cumprido_em"
        )

        ultimo = _converter_data(
            ultimo_original
        )

        ativo = bool(

            ultimo is not None

            and ultimo >= limite_atividade
        )

        robos[codigo] = {

            "nome": item.get(
                "robo",
                f"Robô {codigo}"
            ),

            "ultimo_cumprido_em": ultimo,

            "ultima_execucao_formatada": (
                formatar_data_execucao(
                    ultimo_original
                )
            ),

            "status": (
                "Ativo"
                if ativo
                else "Inativo"
            ),

            "ativo": ativo,

            "eventos": [],

            "total": 0,

            "grupos": 0,

            "meta_diaria": metas.get(
                codigo,
                0
            ),

            "percentual_meta": 0,

            "faltam_meta": metas.get(
                codigo,
                0
            ),
        }

    for item in eventos_rpa:

        codigo = item.get(
            "codigo_robo"
        )

        if codigo not in robos:
            continue

        quantidade = int(
            item.get("qtd") or 0
        )

        robos[codigo]["eventos"].append(
            item
        )

        robos[codigo]["total"] += (
            quantidade
        )

        robos[codigo]["grupos"] += 1

    for robo in robos.values():

        meta = robo["meta_diaria"]

        total = robo["total"]

        robo["percentual_meta"] = (

            round(
                (total / meta) * 100,
                1
            )

            if meta > 0

            else 0
        )

        robo["faltam_meta"] = max(
            meta - total,
            0
        )

    total_eventos = sum(

        robo["total"]

        for robo in robos.values()
    )

    robos_ativos = sum(

        1

        for robo in robos.values()

        if robo["ativo"]
    )

    return render(

        request,

        "portal/dashboard_rpa.html",

        {

            "robos": robos,

            "total_eventos": total_eventos,

            "total_robos": len(
                robos
            ),

            "robos_ativos": robos_ativos,

            "sincronizando": cache.sincronizando,

            "ultima_atualizacao": (
                cache.ultima_atualizacao
            ),

            "ultimo_erro": cache.ultimo_erro,
        },
    )


@login_required(login_url="login")
@require_POST
def atualizar_dashboard_rpa(request):

    try:

        iniciou = _iniciar_sincronizacao_rpa()

        return JsonResponse({

            "ok": True,

            "sincronizando": iniciou,

            "mensagem": (

                "Atualização iniciada."

                if iniciou

                else "Já existe uma atualização em andamento."
            ),
        })

    except Exception:

        logger.exception(
            "Erro ao solicitar atualização do dashboard RPA"
        )

        return JsonResponse({

            "ok": False,

            "mensagem": (
                "Não foi possível iniciar a atualização."
            ),

        }, status=500)


@login_required(login_url="login")
def status_dashboard_rpa(request):

    cache, _ = CacheDashboardRPA.objects.get_or_create(

        chave="dashboard_rpa",

        defaults={
            "dados": {}
        },
    )

    ultima_atualizacao = None

    if cache.ultima_atualizacao:

        ultima_atualizacao = timezone.localtime(

            cache.ultima_atualizacao

        ).strftime(
            "%d/%m/%Y às %H:%M:%S"
        )

    return JsonResponse({

        "sincronizando": cache.sincronizando,

        "ultima_atualizacao": (
            ultima_atualizacao
        ),

        "ultimo_erro": cache.ultimo_erro,
    })