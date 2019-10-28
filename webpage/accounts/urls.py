from django.urls import include, path
from django.contrib.auth import views as authViews
from . import views

urlpatterns = [
    path('user/<slug:username>',        views.account,                                                              name = 'account'),
    path('login',                       authViews.LoginView.as_view(template_name = 'accounts/login.html'),         name = 'login'),
    path('logout',                      authViews.LogoutView.as_view(template_name = 'accounts/logout.html'),       name = 'logout'),
]
