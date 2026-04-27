from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ParkingSpot
from .serializers import ParkingSpotSerializer

# ──────────────────────────────────────────
# AYARLAR
# ──────────────────────────────────────────
API_KEY      = "super-secret-key-123"   # tubitak.py ile eşleşmeli
SENSOR_COUNT = 5                        # Beklenen maksimum sensör sayısı


def _check_api_key(request) -> bool:
    """Header veya query param üzerinden API key doğrular."""
    key = request.headers.get("X-API-Key") or request.GET.get("api_key", "")
    return key == API_KEY


# ──────────────────────────────────────────
# 1. Park yeri listesi — Mobil & Dashboard
# ──────────────────────────────────────────
@api_view(["GET"])
def get_parking_spots(request):
    """
    Tüm park yerlerini döner.
    Opsiyonel filtre: ?status=empty | ?status=occupied
    """
    spots = ParkingSpot.objects.all().order_by("spot_number")

    status_filter = request.GET.get("status")
    if status_filter == "empty":
        spots = spots.filter(is_occupied=False)
    elif status_filter == "occupied":
        spots = spots.filter(is_occupied=True)

    serializer = ParkingSpotSerializer(spots, many=True)

    # Özet istatistikleri de ekle
    total    = spots.count()
    occupied = spots.filter(is_occupied=True).count()
    return Response({
        "spots":    serializer.data,
        "summary": {
            "total":    total,
            "occupied": occupied,
            "empty":    total - occupied,
        },
    })


# ──────────────────────────────────────────
# 2. IoT veri güncelleme — Raspberry Pi / LoRa
# ──────────────────────────────────────────
@api_view(["POST"])
def update_parking_spots(request):
    """
    Cihazdan gelen payload'ı işler.
    Beklenen body: {"payload": "10110", "timestamp": "2025-06-01T12:00:00"}

    Güvenlik: X-API-Key header'ı zorunlu.
    Esneklik: 1–SENSOR_COUNT arası uzunluktaki payload kabul edilir.
    """
    # API key kontrolü
    if not _check_api_key(request):
        return Response({"error": "Yetkisiz erişim."}, status=401)

    payload   = request.data.get("payload", "")
    timestamp = request.data.get("timestamp")   # opsiyonel

    # Validasyon
    if not payload:
        return Response({"error": "payload alanı boş olamaz."}, status=400)

    if not all(c in "01" for c in payload):
        return Response({"error": "payload sadece 0 ve 1 içerebilir."}, status=400)

    if len(payload) > SENSOR_COUNT:
        return Response(
            {"error": f"payload çok uzun. Beklenen maksimum: {SENSOR_COUNT}"},
            status=400,
        )

    # Veritabanını güncelle
    updated = []
    for i, status_char in enumerate(payload):
        is_occupied = status_char == "1"
        spot, created = ParkingSpot.objects.update_or_create(
            spot_number=i + 1,
            defaults={
                "is_occupied":  is_occupied,
                "last_updated": timezone.now(),
            },
        )
        updated.append({
            "spot_number": spot.spot_number,
            "is_occupied": spot.is_occupied,
            "action":      "created" if created else "updated",
        })

    occupied = sum(1 for s in updated if s["is_occupied"])
    return Response({
        "message":   f"{len(updated)} sensör verisi işlendi.",
        "received_at": timestamp or timezone.now().isoformat(),
        "updated":   updated,
        "summary":   {
            "total":    len(updated),
            "occupied": occupied,
            "empty":    len(updated) - occupied,
        },
    }, status=200)


# ──────────────────────────────────────────
# 3. Sistem durumu — Bağlantı testi
# ──────────────────────────────────────────
@api_view(["GET"])
def health_check(request):
    """Raspberry Pi'nin bağlantıyı test etmesi için basit endpoint."""
    spot_count = ParkingSpot.objects.count()
    return Response({
        "status":      "ok",
        "server_time": timezone.now().isoformat(),
        "spot_count":  spot_count,
    })


# ──────────────────────────────────────────
# 4. Web dashboard
# ──────────────────────────────────────────
def dashboard(request):
    return render(request, "dashboard.html")