from django.urls import path
from . import views
from . views import add_vehicle, export_parking_report_csv


urlpatterns = [
    path('', views.home, name='home'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('sessions/', views.parking_sessions, name='parking_sessions'),
    path('register/', views.register, name='register'),
    path('add_vehicle/', add_vehicle, name='add_vehicle'),
    path('find_vehicle/', views.find_vehicle, name='find_vehicle'),
    path('vehicle_entry', views.start_parking_session, name='vehicle_entry'),
    path('vehicle_exit', views.end_parking_session, name='vehicle_exit'),
    path('start_parking/<int:vehicle_id>/', views.start_parking_session, name='start_parking_session'),
    path('end_parking/<int:vehicle_id>/', views.end_parking_session, name='end_parking_session'),
    path('parking_status/', views.parking_status, name='parking_status'),
    path('export/parking_report/', export_parking_report_csv, name='export_parking_report_csv'),
    path('capture_image/', views.capture_image, name='capture_image'),
    path('about_us/', views.about_us, name='about_us'),
]





