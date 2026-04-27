from rest_framework import serializers
from .models import ParkingSpot

class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = ["spot_number", "is_occupied", "last_updated"]