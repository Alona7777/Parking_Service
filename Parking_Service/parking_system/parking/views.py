import base64
import csv
from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
# from .vision import detect_license_plate
from .forms import ParkingImageForm, VehicleSearchForm, StartParkingSessionForm, EndParkingSessionForm

import cv2
import numpy as np
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Value
from django.db.models.functions import Replace, Trim, Upper
from django.http import HttpResponse
from django.utils import timezone

# from .vision import detect_license_plate
from .forms import ParkingImageForm, VehicleSearchForm, StartParkingSessionForm, EndParkingSessionForm, UserProfileForm, \
    TransactionForm
from .forms import UserRegisterForm, VehicleForm
from .models import Vehicle, ParkingSession, ParkingRate, ParkingSpot, UserProfile, Transaction, ParkingImage
from .vision import detect_and_recognize_license_plates

from django.core.files.base import ContentFile
from django.views.decorators.cache import cache_page
import logging

logger = logging.getLogger(__name__)



def home(request):
    rates = ParkingRate.objects.all()
    return render(request, 'home.html', {'rates': rates})


@login_required
def edit_profile(request):
    # Создаем профиль, если его нет
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Обработка данных формы
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'form': form})


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'transaction_history.html', {'transactions': transactions})


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
    response = HttpResponse(content_type='text/csv')
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
            try:
                rate = session.vehicle.get_parking_rate()
            except ParkingRate.DoesNotExist:
                rate = Decimal('0.00')
                print(f"Warning: No parking rate found for vehicle type '{session.vehicle.vehicle_type}'.")

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


def start_parking_session(request):
    if request.method == "POST":
        form = StartParkingSessionForm(request.POST)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicle']
            entry_time = form.cleaned_data['entry_time']

            # Логика для поиска парковочного места
            if vehicle.subscription_end_date and vehicle.subscription_end_date >= timezone.now().date():
                if vehicle.parking_spot_id:
                    spot = ParkingSpot.objects.filter(id=vehicle.parking_spot_id).first()
                else:
                    spot = ParkingSpot.objects.filter(spot_type='SUBSCRIPTION', is_occupied=False).first()

            elif vehicle.is_disabled:
                spot = ParkingSpot.objects.filter(spot_type='DISABLED', is_occupied=False).first()
                if not spot:
                    spot = ParkingSpot.objects.filter(spot_type='HOURLY', is_occupied=False).first()
            else:
                spot = ParkingSpot.objects.filter(spot_type='HOURLY', is_occupied=False).first()

            if spot:
                spot.is_occupied = True
                spot.occupied_by = vehicle
                spot.occupied_since = entry_time
                spot.save()

                session = ParkingSession(vehicle=vehicle, parking_spot=spot, entry_time=entry_time)
                session.save()
                vehicle.parking_spot = spot
                vehicle.save()

                return redirect('parking_status')
            else:
                return render(request, 'no_parking_spots.html')
    else:
        form = StartParkingSessionForm()

    return render(request, 'vehicle_entry.html', {'form': form})


def end_parking_session(request):
    if request.method == "POST":
        form = EndParkingSessionForm(request.POST)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicle']
            exit_time = form.cleaned_data['exit_time']

            session = ParkingSession.objects.filter(vehicle=vehicle, exit_time__isnull=True).first()

            if session:
                session.exit_time = exit_time
                session.save()

                # Освобождаем парковочное место
                spot = session.parking_spot
                if spot:
                    spot.is_occupied = False
                    spot.occupied_by = None
                    spot.occupied_since = None
                    spot.save()

                if not (vehicle.subscription_end_date and vehicle.subscription_end_date >= exit_time.date()):
                    vehicle.parking_spot = None

                vehicle.save()

            return redirect('parking_status')
    else:
        form = EndParkingSessionForm()

    return render(request, 'vehicle_exit.html', {'form': form})


def parking_status(request):
    spots = ParkingSpot.objects.all().order_by('number')
    return render(request, 'parking_status.html', {'spots': spots})



# @cache_page(60 * 15)
# def capture_image(request):
#     if request.method == 'POST':
#         # Відкриття вебкамери
#         cap = cv2.VideoCapture(0)
#         # # "Прогреваем" камеру, чтобы снимок не был тёмным
#         # for i in range(30):
#         #     cap.read()
#         if not cap.isOpened():
#             return render(request, 'capture_image.html', {'error': 'Could not access the camera.'})

#         # Захоплення кадру
#         ret, frame = cap.read()
#         cap.release()

#         if not ret:
#             return render(request, 'capture_image.html', {'error': 'Could not capture image.'})

#         # Обробка зображення для розпізнавання номерного знака
#         license_plates, annotated_image = detect_and_recognize_license_plates(frame)
#         combined_plates = ', '.join(license_plates)

#         # Кодування зображення у формат Base64 для виведення на сторінці
#         _, buffer = cv2.imencode('.jpg', annotated_image)
#         image_base64 = base64.b64encode(buffer).decode('utf-8')

#         return render(request, 'capture_image.html', {
#             'license_plate': combined_plates,
#             'annotated_image_base64': image_base64
#         })

#     return render(request, 'capture_image.html')

# def about_us(request):
#     return render(request, 'about_us.html')


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicle']
            start_date = form.cleaned_data['start_date']
            # is_disabled = form.cleaned_data['is_disabled']
            parking_spot = form.cleaned_data['parking_spot']

            # Check if the vehicle is blocked
            if vehicle.is_blocked:
                messages.error(request, "Выбранное авто заблокировано.")
                return redirect('add-transaction')

            # Get user profile and check balance
            user_profile = UserProfile.objects.get(user=request.user)
            parking_rate = ParkingRate.objects.get(vehicle_type=vehicle.vehicle_type)
            rate = parking_rate.rental_rate

            if user_profile.monetary_limit < rate:
                messages.error(request, "Пополните баланс.")
                return redirect('add-transaction')

            if parking_spot:
                # Save parking spot and subscription end date to vehicle
                vehicle.parking_spot = parking_spot
                vehicle.subscription_end_date = start_date + timedelta(days=30)
                vehicle.save()

                # Mark the parking spot as occupied
                parking_spot.is_occupied = True
                parking_spot.occupied_by = vehicle
                parking_spot.occupied_since = start_date
                parking_spot.save()

            # Create a new transaction
            # if not is_blocked:
            Transaction.objects.create(
                user=request.user,
                transaction_type='SUBSCRIPTION_FEE',
                amount=rate,
                description=f"Subscription fee for vehicle {vehicle.license_plate}"
            )
            # Deduct money from the user's balance
            user_profile.monetary_limit -= rate
            user_profile.save()

            # Handle disabled vehicle
            # if is_disabled:
            #     vehicle.is_disabled = True
            #     vehicle.save()

            messages.success(request, "Абонемент успешно оформлен.")
            return redirect('home')

    else:
        form = TransactionForm(user=request.user)

    return render(request, 'add_transaction.html', {'form': form})
  
