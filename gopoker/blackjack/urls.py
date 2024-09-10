from django.urls import path
from . import views

app_name = "bj"
urlpatterns = [
    path('', views.index, name='index'),
    path('room/<room_id>/', views.display_room, name="room"),
    path('room/<room_id>/join', views.join_room, name="join"),
    path('room/<room_id>/leave', views.leave_room, name="leave"),
    path('room/<room_id>/hit/', views.hit, name='hit'),
    path('room/<room_id>/stand/', views.stand, name='stand'),
]
