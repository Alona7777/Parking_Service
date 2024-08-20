from django.core.management.base import BaseCommand
from parking.models import ParkingSpot

class Command(BaseCommand):
    help = 'Populate the database with parking spots'

    def handle(self, *args, **kwargs):
        # Создание парковочных мест для абонемента
        for i in range(1, 21):
            ParkingSpot.objects.create(number=i, spot_type='SUBSCRIPTION')

        # Создание парковочных мест для инвалидов
        for i in range(21, 27):
            ParkingSpot.objects.create(number=i, spot_type='DISABLED')

        # Создание парковочных мест для почасовой стоянки
        for i in range(27, 51):
            ParkingSpot.objects.create(number=i, spot_type='HOURLY')

        self.stdout.write(self.style.SUCCESS('Successfully populated parking spots'))