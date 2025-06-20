from rest_framework import serializers
from .models import VehicleLog

class VehicleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLog
        fields = ['id', 'timestamp', 'action']
