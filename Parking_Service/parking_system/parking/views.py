from django.shortcuts import render, redirect
from .models import Vehicle, ParkingSession, ParkingImage, ParkingRate
from .vision import detect_license_plate
from .forms import ParkingImageForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, VehicleForm
from django.contrib.auth.decorators import login_required


def home(request):
    rates = ParkingRate.objects.all()
    return render(request, 'home.html', {'rates': rates})


def upload_image(request):
    if request.method == 'POST':
        form = ParkingImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            license_plate = detect_license_plate(image.image.path)
            image.license_plate = license_plate
            image.save()
            return render(request, 'upload_image.html', {'license_plate': license_plate})
    return render(request, 'upload_image.html')


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





