from django.urls import path
from . import views

urlpatterns = [
    path('spots/',   views.get_parking_spots,    name='get_spots'),
    path('update/',  views.update_parking_spots,  name='update_spots'),
    path('health/',  views.health_check,          name='health_check'),
]