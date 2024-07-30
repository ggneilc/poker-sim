from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.start, name='start'),
    path('hit/', views.hit, name='hit'),
    path('stand/', views.stand, name='stand'),
]
