from django.db import models


class CacheDashboardRPA(models.Model):
    chave = models.CharField(
        max_length=50,
        unique=True,
        default="dashboard_rpa",
    )

    dados = models.JSONField(default=dict, blank=True)

    ultima_atualizacao = models.DateTimeField(
        null=True,
        blank=True,
    )

    sincronizando = models.BooleanField(default=False)

    inicio_sincronizacao = models.DateTimeField(
        null=True,
        blank=True,
    )

    ultimo_erro = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Cache do Dashboard RPA"
        verbose_name_plural = "Cache do Dashboard RPA"

    def __str__(self):
        return self.chave