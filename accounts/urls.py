from django.urls import path
from django.contrib.auth import views as auth_views

from .views import signup_view, login_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', signup_view, name='signup')
]
