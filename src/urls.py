from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('data_access/', views.data_access, name='data_access'),
    path('logout/', views.logout, name='logout'),
    path('google_login/', views.google_login, name='google_login'),
    path('oauth2callback/', views.google_callback, name='google_callback'),
]
