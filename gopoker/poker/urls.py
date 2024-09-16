from django.urls import path
from . import views

app_name = "poker"
urlpatterns = [
    path('', views.index, name='index'),
    path('room/<room_id>/', views.displayRoom, name="room"),
    path('room/<room_id>/join', views.joinRoom, name="join"),
    path('room/<room_id>/leave', views.leaveRoom, name="leave"),
    path('room/<room_id>/renderseat', views.renderSeat, name='renderseat'),
    path('room/<room_id>/start/', views.startGame, name='start'),
    path('room/<room_id>/stop/', views.stopGame, name='stop'),
    path('room/<room_id>/chat/', views.chatView, name='chat')
]
