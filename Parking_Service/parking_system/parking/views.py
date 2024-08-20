import cv2
import numpy as np
import csv
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Vehicle, ParkingSession, ParkingImage, ParkingRate
# from .vision import get_plates
# from .forms import ParkingImageForm
# from .vision import detect_license_plate, get_plates
from .forms import ParkingImageForm, VehicleSearchForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, VehicleForm
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Replace, Trim, Upper
from django.db.models import Value
from .vision import detect_and_recognize_license_plates
import base64



def home(request):
    rates = ParkingRate.objects.all()
    return render(request, 'home.html', {'rates': rates})


def upload_image(request):
    if request.method == 'POST':
        form = ParkingImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            nparr = np.frombuffer(image_file.read(), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Используем функцию из vision.py
            license_plates, annotated_image = detect_and_recognize_license_plates(img)
            combined_plates = ', '.join(license_plates)

            # Кодирование изображения в Base64
            _, buffer = cv2.imencode('.jpg', annotated_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            return render(request, 'upload_image.html', {
                'license_plate': combined_plates,
                'annotated_image_base64': image_base64
            })
    else:
        form = ParkingImageForm()

    return render(request, 'upload_image.html', {'form': form})

# def upload_image(request):
#     if request.method == 'POST':
#         form = ParkingImageForm(request.POST, request.FILES)
#         if form.is_valid():
#             image_file = form.cleaned_data['image']
#             nparr = np.frombuffer(image_file.read(), np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             license_plates = get_plates(img)
#             combined_plates = ' '.join(license_plates)
#             return render(request, 'upload_image.html', {'license_plate': combined_plates})
#     return render(request, 'upload_image.html', {'form': ParkingImageForm()})


@login_required(login_url='login')
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user

            # Проверка уникальности номера
            cleaned_plate = form.cleaned_data['license_plate'].replace(" ", "").replace("-", "").upper()
            existing_vehicles = Vehicle.objects.annotate(
                cleaned_license_plate=Trim(
                    Replace(Replace(Upper('license_plate'), Value(" "), Value("")), Value("-"), Value("")))
            ).filter(cleaned_license_plate=cleaned_plate)

            if existing_vehicles.exists():
                form.add_error('license_plate', 'This license plate is already registered.')
            else:
                vehicle.save()
                return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'add_vehicle.html', {'form': form})


@login_required(login_url='login')
def vehicle_list(request):
    if request.user.is_staff:
        vehicles = Vehicle.objects.all()
    else:
        vehicles = Vehicle.objects.filter(owner=request.user)
    return render(request, 'vehicle_list.html', {'vehicles': vehicles})


@login_required(login_url='login')
def export_parking_report_csv(request):
    response = HttpResponse(content_type='csv')
    response['Content-Disposition'] = 'attachment; filename="parking_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Vehicle', 'Owner', 'Entry time', 'Exit time', 'Total duration', 'Cost'])

    if request.user.is_staff:
        sessions = ParkingSession.objects.all()
    else:
        sessions = ParkingSession.objects.filter(vehicle__owner=request.user)

    for session in sessions:
        if session.total_duration is not None:
            duration_in_hours = Decimal(session.total_duration.total_seconds()) / Decimal(3600)
            rate = session.vehicle.get_parking_rate()
            cost = duration_in_hours * rate

            writer.writerow([
                session.vehicle.license_plate,
                session.vehicle.owner.username,
                session.entry_time,
                session.exit_time or "In Progress",
                session.total_duration,
                f"{cost:.2f} USD"
            ])
        else:
            writer.writerow([
                session.vehicle.license_plate,
                session.vehicle.owner.username,
                session.entry_time,
                "In Progress",
                "In Progress",
                "In Progress"
            ])

    return response


@login_required(login_url='login')
def parking_sessions(request):
    if request.user.is_staff:
        sessions = ParkingSession.objects.all()
    else:
        sessions = ParkingSession.objects.filter(vehicle__owner=request.user)

    return render(request, 'parking_sessions.html', {'sessions': sessions})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def find_vehicle(request):
    form = VehicleSearchForm(request.GET or None)
    result = None

    if form.is_valid():
        cleaned_query_plate = form.cleaned_data['license_plate']

        # Очистка и форматирование номеров в базе данных
        cleaned_vehicles = Vehicle.objects.annotate(
            cleaned_license_plate=Trim(
                Replace(Replace(Upper('license_plate'), Value(" "), Value("")), Value("-"), Value("")))
        ).select_related('owner')

        try:
            # Поиск автомобиля по очищенному номеру
            vehicle = cleaned_vehicles.get(cleaned_license_plate=cleaned_query_plate)
            result = {
                'license_plate': vehicle.license_plate,
                'vehicle_type': vehicle.vehicle_type,
                'owner_id': vehicle.owner.id,
                'username': vehicle.owner.username,
                'first_name': vehicle.owner.first_name,
                'last_name': vehicle.owner.last_name,
            }
        except Vehicle.DoesNotExist:
            result = None

    return render(request, 'find_nomer.html', {'form': form, 'result': result})