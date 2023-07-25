from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('token-refresh/', views.token_refresh, name='token_refresh'),
    path('data-access/', views.data_access, name='data_access'),
    path("login_2fa/", views.login_2fa, name="login_2fa"),
    path("setup_2fa/", views.setup_2fa, name="setup_2fa"),
    path("verify_2fa/", views.verify_2fa, name="verify_2fa"),
]
