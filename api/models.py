from django.db import models
from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class ParkingSpot(models.Model):
    spot_number  = models.IntegerField(unique=True)
    is_occupied  = models.BooleanField(default=False)
    last_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["spot_number"]

    def __str__(self):
        status = "Dolu" if self.is_occupied else "Boş"
        return f"P{self.spot_number} — {status}"
    
class Driver(models.Model):
    full_name = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=20, unique=True)
    penalty_points = models.IntegerField(default=0) # YENİ: Ceza puanı sistemi
    is_banned = models.BooleanField(default=False)  # YENİ: 3 puanda banlanır

class Reservation(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    spot = models.ForeignKey('ParkingSpot', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    @property
    def is_expired(self):
        # Eğer şu anki zaman, rezervasyon saatinden 15 dakika sonrasından büyükse: Süre doldu!
        return now() > self.created_at + timedelta(minutes=15)