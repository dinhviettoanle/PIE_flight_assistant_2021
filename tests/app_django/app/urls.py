from django.urls import path
from . import views

urlpatterns = [
    path('app/', views.app, name='app'),
    path('', views.redirect_app, name='redirect_app'),

]