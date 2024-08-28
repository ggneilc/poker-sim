from django.urls import path
from . import views

app_name = "poker"
urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.startGame, name='start'),
    path('stop/', views.stopGame, name='stop'),
    path('chat/', views.chatView, name='chat')
]
