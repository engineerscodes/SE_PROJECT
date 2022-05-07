from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('login/',views.login,name="login"),
    path('reg/',views.reg,name="REG"),
    path('logout/',views.logout,name="LOGOUT"),
    path('activate/<uidb64>/<token>',views.AUTHUSERNAME,name="activate"),
    path('password/reset/',views.resetPassword,name="reset"),
    path('reset/<uidb64>/<token>',views.vali_reset_pass,name="reset_pass")
]