from django.urls import path
from . import views
from .views import add_vehicle, export_parking_report_csv, transaction_history, add_transaction, upload_and_find_vehicle

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
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('transaction_history/', transaction_history, name='transaction_history'),
    path('add_transaction/', add_transaction, name='add_transaction'),
    path('upload-and-find/', upload_and_find_vehicle, name='upload-and-find-vehicle'),
    path('export/parking_report/', export_parking_report_csv, name='export_parking_report_csv'),
    path('about_us/', views.about_us, name='about_us'),
    path('capture_image/', views.capture_image, name='capture_image'),
    path('start_parking_session_image/', views.start_parking_session_image, name='start_parking_session_image'),
    path('end_parking_session_image/', views.end_parking_session_image, name='end_parking_session_image'),


]





