from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.startGame, name='start'),
    path('stop/', views.stopGame, name='stop'),
]
