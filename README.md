# 🚗 Akıllı Otopark Sistemi (Smart Parking System)

Bu proje, otoparklardaki araç doluluk durumunu sensörlerle okuyup, sürücülere gerçek zamanlı olarak mobil uygulama üzerinden sunan **uçtan uca (end-to-end) bir IoT ve yazılım çözümüdür.** Sistem; donanım, sunucu (backend) ve mobil arayüz (frontend) olmak üzere üç ana katmandan oluşmaktadır.

---

## 🏗️ Sistem Mimarisi ve Çalışma Mantığı

Proje donanım maliyetlerini düşürmek ve ağ yükünü hafifletmek için yenilikçi bir **"Depo Şefi & Kurye" (Hibrit IoT)** mimarisi kullanır:

1. **Raspberry Pi (Sensör Yöneticisi):** Otoparktaki HC-SR04 ultrasonik sensörleri okur. İnternete bağlanmaz. Araçların mesafesini ölçer, `10110` (Dolu/Boş) formatında bir veri paketi hazırlar ve bunu seri port (USB) üzerinden NodeMCU'ya iletir.
2. **NodeMCU ESP8266 (Wi-Fi Köprüsü):** Raspberry Pi'den gelen saf veriyi dinler. Veriyi aldığı an kendi üzerindeki Wi-Fi çipini kullanarak Django API sunucusuna POST isteği atar.
3. **Django Sunucu (Backend):** NodeMCU'dan gelen anlık verileri alır, veritabanına işler ve mobil uygulamanın tüketebileceği bir REST API sunar.
4. **Flutter Mobil Uygulama (Frontend):** Sürücü
