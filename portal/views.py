from django.shortcuts import render
from .cpj import consultar_usuarios, consultar_concluidos,testar_gateway


def home(request):
    return render(request, 'portal/home.html')

def relatorios(request):
    total_usuarios = consultar_usuarios()

    return render(
        request,
        'portal/relatorios.html',
        {
            'total_usuarios': total_usuarios,
        }
    )
    
    
def guia_condenacao(request):

    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    evento = request.GET.get('evento')

    colunas = []
    resultados = []
    total_registros = 0

    if data_inicio and data_fim and evento:

        colunas, resultados_completos = consultar_concluidos(
            data_inicio,
            data_fim,
            evento
        )

        total_registros = len(resultados_completos)

        resultados = resultados_completos[:20]

    return render(
        request,
        'portal/guia_condenacao.html',
        {
            'colunas': colunas,
            'resultados': resultados,
            'total_registros': total_registros,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'evento': evento,
        }
    )
    
def teste_gateway(request):
    resultado = testar_gateway()
    return render(
        request,
        'portal/home.html',
        {'resultado_gateway': resultado}
    )