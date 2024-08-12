from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('sessions/', views.parking_sessions, name='parking_sessions'),
]
