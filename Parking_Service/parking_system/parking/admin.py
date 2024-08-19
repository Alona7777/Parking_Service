from django.contrib import admin
from .models import Vehicle, ParkingSession, ParkingRate

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'vehicle_type', 'is_blocked')
    list_filter = ('vehicle_type', 'is_blocked')
    search_fields = ('license_plate', 'owner__username')
    list_editable = ('is_blocked',)

# admin.site.register(Vehicle)
admin.site.register(ParkingSession)
admin.site.register(ParkingRate)
