from django import forms
from django.contrib import admin
from .models import Vehicle, ParkingSession, ParkingRate, ParkingSpot

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'vehicle_type', 'is_blocked', 'parking_spot', 'subscription_end_date', 'is_disabled')
    list_filter = ('vehicle_type', 'is_blocked')
    search_fields = ('license_plate', 'owner__username')
    list_editable = ('is_blocked',)

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('number', 'spot_type', 'is_occupied', 'occupied_by', 'occupied_since')

@admin.register(ParkingSession)
class ParkingSessionAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'entry_time', 'exit_time', 'total_duration', 'parking_spot')
    fields = ('vehicle', 'entry_time', 'exit_time', 'total_duration', 'parking_spot')  # Если поля не отображаются

@admin.register(ParkingRate)
class ParkingRateAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'rate_per_hour')