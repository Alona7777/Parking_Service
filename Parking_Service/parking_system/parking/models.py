from django.db import models
from django.contrib.auth.models import User


class Vehicle(models.Model):
    license_plate = models.CharField(max_length=12, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=20, unique=False, default='car')

    def __str__(self):
        return f"{self.license_plate} - {self.owner}"

    def get_parking_rate(self):
        rate = ParkingRate.objects.get(vehicle_type=self.vehicle_type)
        return rate.rate_per_hour


class ParkingSession(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    total_duration = models.DurationField(null=True, blank=True)

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
    VEHICLE_TYPE_CHOICES = [
        ('track', 'Track'),
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('yaht', 'Yacht')
    ]

    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, unique=False)
    rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.get_vehicle_type_display()} - {self.rate_per_hour} per hour"





