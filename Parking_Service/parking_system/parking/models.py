from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User


class ParkingSpot(models.Model):
    SPOT_TYPE_CHOICES = [
        ('SUBSCRIPTION', 'Subscription'),
        ('DISABLED', 'Disabled'),
        ('HOURLY', 'Hourly'),
    ]

    number = models.IntegerField(unique=True)
    spot_type = models.CharField(max_length=12, choices=SPOT_TYPE_CHOICES)
    is_occupied = models.BooleanField(default=False)
    occupied_by = models.ForeignKey('Vehicle', null=True, blank=True, on_delete=models.SET_NULL)
    occupied_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Spot {self.number} ({self.get_spot_type_display()})"

class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('bus', 'Bus'),
        ('truck', 'Truck'),
        ('yacht', 'Yacht'),
    ]

    license_plate = models.CharField(max_length=12, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    is_blocked = models.BooleanField(default=False)   # Поле для блокировки авто
    parking_spot = models.ForeignKey(ParkingSpot, null=True, blank=True, on_delete=models.SET_NULL)
    subscription_end_date = models.DateField(null=True, blank=True)
    is_disabled = models.BooleanField(default=False)  # Флаг принадлежности инвалиду
    

    def __str__(self):
        return f"{self.license_plate} - {self.owner} - {self.vehicle_type}"

    def get_parking_rate(self):
        try:
            rate = ParkingRate.objects.get(vehicle_type=self.vehicle_type)
            return rate.rate_per_hour
        except ParkingRate.DoesNotExist:
            return Decimal('0.00')

class ParkingSession(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    total_duration = models.DurationField(null=True, blank=True)
    parking_spot = models.ForeignKey(ParkingSpot, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Session for {self.vehicle.license_plate} at {self.entry_time}"

    def save(self, *args, **kwargs):
        if self.entry_time and self.exit_time:
            self.total_duration = self.exit_time - self.entry_time
        super().save(*args, **kwargs)

class ParkingImage(models.Model):
    image = models.ImageField(upload_to='parking_images/')
    license_plate = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.license_plate if self.license_plate else 'Unknown'


class ParkingRate(models.Model):
    vehicle_type = models.CharField(max_length=20, unique=True, choices=[
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('bus', 'Bus'),
        ('truck', 'Truck'),
        ('yacht', 'Yacht'),
    ])

    # vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, unique=False)
    rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.get_vehicle_type_display()} - {self.rate_per_hour} per hour"





