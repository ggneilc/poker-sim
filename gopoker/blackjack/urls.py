from django.urls import path
from . import views

app_name = "bj"
urlpatterns = [
    path('', views.index, name='index'),        # enter url or create room
    path('create/', views.create_room, name='create'),
    path('room/<int:room_id>/', views.display_room, name="room"),
    path('room/<int:room_id>/join', views.join_room, name="join"),
    path('hit/', views.hit, name='hit'),
    path('stand/', views.stand, name='stand'),
]
