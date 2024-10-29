from django import forms
from django.contrib import admin
from .models import Vehicle, ParkingSession, ParkingRate, ParkingSpot, UserProfile, Transaction

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'vehicle_type', 'is_blocked', 'parking_spot', 'subscription_end_date', 'is_disabled')
    list_filter = ('vehicle_type', 'is_blocked')
    search_fields = ('license_plate', 'owner__username')
    list_editable = ('is_blocked', 'parking_spot', 'subscription_end_date', 'is_disabled')

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('number', 'spot_type', 'is_occupied', 'occupied_by', 'occupied_since')

@admin.register(ParkingSession)
class ParkingSessionAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'entry_time', 'exit_time', 'total_duration', 'parking_spot')
    fields = ('vehicle', 'entry_time', 'exit_time', 'total_duration', 'parking_spot')  # If the fields are not displayed

@admin.register(ParkingRate)
class ParkingRateAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'rental_rate', 'rate_per_hour', 'disabled_rate')
    list_editable = ('rental_rate', 'rate_per_hour', 'disabled_rate')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'monetary_limit']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'timestamp', 'description')
    search_fields = ('user__username', 'transaction_type')
