from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import VehicleLog
from .serializers import VehicleLogSerializer
from django.utils.timezone import now, timedelta

@api_view(['POST'])
def log_vehicle(request):
    serializer = VehicleLogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Logged"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_status(request):
    entries = VehicleLog.objects.filter(action='entry').count()
    exits = VehicleLog.objects.filter(action='exit').count()
    current = entries - exits
    return Response({
        "total_entered": entries,
        "total_exited": exits,
        "currently_parked": current
    })

@api_view(['GET'])
def get_recent_vehicles(request):
    logs = VehicleLog.objects.order_by('-timestamp')[:10]
    serializer = VehicleLogSerializer(logs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def vehicles_over_time(request):
    today = now().date()
    data = []
    for i in range(7):
        day = today - timedelta(days=i)
        count = VehicleLog.objects.filter(timestamp__date=day).count()
        data.append({"date": str(day), "count": count})
    return Response(list(reversed(data)))

