# users/urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (LogoutView, PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views
from .views import MyLoginView

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'login/',
        MyLoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change'
    ),
    path(
        'password_change/',
        PasswordResetDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password_reset_confirm/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='reset_confirm'
    ),
    path(
        'password_reset_complete/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='reset_complete'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
