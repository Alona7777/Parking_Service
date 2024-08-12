from rest_framework import serializers
from .models import Vehicle, ParkingSession, ParkingImage


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class ParkingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSession
        fields = '__all__'


class ParkingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingImage
        fields = '__all__'

