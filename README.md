# UASK Yazılım Eğitimi - Otonom İHA Projesi 🚀

Bu depo, **Yıldız Teknik Üniversitesi Uzay ve Aviyonik Sistemler Kulübü (UASK)** yazılım birimi eğitimleri kapsamında hazırlanmış 4 haftalık otonom uçuş ve görüntü işleme görevlerini içermektedir.

Proje, gerçek bir otonomi mimarisi olan **ROS (Robot Operating System)** mantığına sadık kalarak, Windows ortamında tam uyumlu çalışacak şekilde `multiprocessing` (Çoklu İşlem) ve Node (Düğüm) tabanlı OOP mimarisiyle geliştirilmiştir.

## 🗂️ Proje İçeriği (Haftalık Görevler)

* **Hafta 1:** OpenCV ile kamera kurulumu, renk uzayı (HSV) dönüşümleri, mavi/kırmızı nesne tespiti ve ekrana şeffaf kulüp logosu (Alpha Blending) yerleştirme.
* **Hafta 2:** Pymavlink ile Mission Planner SITL (Simülasyon) bağlantısı kurma, uçuş modlarını (GUIDED, RTL) değiştirme ve otonom kalkış (Takeoff) algoritmaları.
* **Hafta 3:** Pseudo-ROS Mimarisi. Kamera ve Uçuş kontrol kodlarının iki bağımsız Node (Düğüm) olarak işlemcinin farklı çekirdeklerinde paralel çalıştırılması ve aralarında `Queue` (Topic) üzerinden haberleşme sağlanması.
* **Hafta 4:** Watchdog (Güvenlik Köpeği) entegrasyonu. Kamera düğümünün çökmesi veya iletişimin kopması durumunda İHA'nın 3 saniye içinde durumu fark edip otonom acil iniş (Failsafe RTL) başlatması.

## 🛠️ Kurulum ve Gereksinimler

Proje tamamen Windows ortamında ve standart Python kütüphaneleriyle çalışmak üzere tasarlanmıştır.

**1. Depoyu Klonlayın:**
```bash
git clone [https://github.com/KULLANICI_ADIN/uask-egitim.git](https://github.com/KULLANICI_ADIN/uask-egitim.git)
cd uask-egitim
```

<img width="1316" height="356" alt="uask logo siyah (2)" src="https://github.com/user-attachments/assets/cf7b7716-e45c-49c7-826a-1c76bbb1939c" />

