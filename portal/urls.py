
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="portal/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "",
        views.dashboard_rpa,
        name="dashboard_rpa",
    ),
    path(
        "rpa/atualizar/",
        views.atualizar_dashboard_rpa,
        name="atualizar_dashboard_rpa",
    ),
    path(
        "rpa/status/",
        views.status_dashboard_rpa,
        name="status_dashboard_rpa",
    ),
]
