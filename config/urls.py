from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.http import HttpResponse
from pathlib import Path
from django.conf import settings


def service_worker(request):
    arquivo = Path(settings.BASE_DIR) / "portal" / "static" / "portal" / "service-worker.js"

    resposta = HttpResponse(
        arquivo.read_text(encoding="utf-8"),
        content_type="application/javascript"
    )

    resposta["Service-Worker-Allowed"] = "/"

    return resposta


urlpatterns = [
    path("admin/", admin.site.urls),
    path("service-worker.js", service_worker),
    path("", include("portal.urls")),
]