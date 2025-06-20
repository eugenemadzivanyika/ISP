from django.urls import path
from . import views


urlpatterns = [
    path('vehicles/log/', views.log_vehicle),
    path('status/', views.get_status),
    path('vehicles/recent/', views.get_recent_vehicles),
    path('vehicles/stats/', views.vehicles_over_time),
]
