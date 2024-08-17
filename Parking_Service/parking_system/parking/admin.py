from django.contrib import admin
from .models import Vehicle, ParkingSession, ParkingRate

admin.site.register(Vehicle)
admin.site.register(ParkingSession)
admin.site.register(ParkingRate)


