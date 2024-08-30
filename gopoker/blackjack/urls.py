from django.urls import path
from . import views

app_name = "bj"
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_room, name='create'),
    path('room/<int:room_id>/', views.display_room, name="room"),
    path('room/<int:room_id>/join', views.join_room, name="join"),
    path('room/<int:room_id>/hit/', views.hit, name='hit'),
    path('room/<int:room_id>/stand/', views.stand, name='stand'),
]
