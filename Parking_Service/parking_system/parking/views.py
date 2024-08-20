import cv2
import numpy as np
import csv
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Vehicle, ParkingSession, ParkingImage, ParkingRate
from .vision import get_plates
from .forms import ParkingImageForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, VehicleForm
from django.contrib.auth.decorators import login_required


def home(request):
    rates = ParkingRate.objects.all()
    return render(request, 'home.html', {'rates': rates})


# def upload_image(request):
#     if request.method == 'POST':
#         form = ParkingImageForm(request.POST, request.FILES)
#         if form.is_valid():
#             image = form.cleaned_data['image']
#             # image = form.save()
#             license_plate = detect_license_plate(image)
#             combined_plates = ' '.join(license_plate)
#             # image.license_plate = license_plate
#             # image.save()
#             return render(request, 'upload_image.html', {'license_plate': combined_plates })
#     return render(request, 'upload_image.html')


def upload_image(request):
    if request.method == 'POST':
        form = ParkingImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            nparr = np.frombuffer(image_file.read(), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            license_plates = get_plates(img)
            combined_plates = ' '.join(license_plates)
            return render(request, 'upload_image.html', {'license_plate': combined_plates})
    return render(request, 'upload_image.html', {'form': ParkingImageForm()})

@login_required(login_url='login')
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
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


