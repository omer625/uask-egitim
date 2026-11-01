import cv2
import numpy as np
import time
from multiprocessing import Process, Queue
from pymavlink import mavutil

# =========================================================================
# SÜREÇ 1: GÖRÜNTÜ İŞLEME (Kamera ve Renk Tespiti)
# =========================================================================
def goru_sureci(kuyruk):
    cap = cv2.VideoCapture(2) # Kendi kamera indeksine göre ayarlayabilirsin (0 veya 2)
    
    # Sürekli aynı mesajı spamlememek için son gönderdiğimiz durumu tutalım
    son_durum = None
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Kırmızı renk kontrolü (Acil İniş)
        maske_kirmizi = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        if cv2.countNonZero(maske_kirmizi) > 500:
            if son_durum != "ACIL_INIS":
                print("[GORU] KIRMIZI tespit edildi! Kuyruğa ACIL_INIS atılıyor...")
                kuyruk.put("ACIL_INIS")
                son_durum = "ACIL_INIS"
        
        # Mavi renk kontrolü (Otonom Kalkış)
        alt_mavi = np.array([90, 100, 100])
        ust_mavi = np.array([130, 255, 255])
        maske_mavi = cv2.inRange(hsv, alt_mavi, ust_mavi)
        
        konturlar, _ = cv2.findContours(maske_mavi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if konturlar:
            en_buyuk = max(konturlar, key=cv2.contourArea)
            if cv2.contourArea(en_buyuk) > 500:
                if son_durum != "KALKIS":
                    print("[GORU] MAVİ tespit edildi! Kuyruğa KALKIS atılıyor...")
                    kuyruk.put("KALKIS")
                    son_durum = "KALKIS"

        cv2.imshow("Entegrasyon - Kamera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# =========================================================================
# SÜREÇ 2: UÇUŞ KONTROLÜ (Pymavlink ve Durum Makinesi)
# =========================================================================
def ucus_sureci(kuyruk):
    print("[UCUS] SITL bağlantısı bekleniyor...")
    master = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
    master.wait_heartbeat()
    print("[UCUS] SITL bağlantısı başarılı!")

    # Uçuş durumumuz: YERDE veya HAVADA
    durum = "YERDE"

    while True:
        # Kuyrukta okunmayı bekleyen mesaj var mı kontrol et (bloklamadan)
        if not kuyruk.empty():
            mesaj = kuyruk.get()
            
            # ACIL_INIS her koşulda en önceliklidir
            if mesaj == "ACIL_INIS":
                print("[UCUS] ACİL İNİŞ (RTL) komutu işleme alınıyor!")
                master.set_mode(master.mode_mapping()['RTL'])
                durum = "INIS"
                
            elif mesaj == "KALKIS" and durum == "YERDE":
                print("[UCUS] Kalkış komutu işleme alınıyor...")
                
                # GUIDED Mod
                master.set_mode(master.mode_mapping()['GUIDED'])
                time.sleep(1)
                
                # ARM Et
                master.arducopter_arm()
                master.motors_armed_wait()
                print("[UCUS] Motorlar ARM edildi.")
                
                # Takeoff (15 Metre)
                master.mav.command_long_send(
                    master.target_system, master.target_component,
                    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
                    0, 0, 0, 0, 0, 0, 15
                )
                durum = "HAVADA"
                print("[UCUS] İHA havada, görev icra ediliyor.")

        time.sleep(0.1)


# =========================================================================
# ANA ÇALIŞTIRMA BLOKU (Windows için Multiprocessing Şartı)
# =========================================================================
if __name__ == '__main__':
    print("Sistem başlatılıyor... Çıkmak için kamera penceresindeyken 'q' tuşuna basın.")
    
    # Süreçler arası haberleşme için kutu (Queue) oluştur
    veri_kuyrugu = Queue()
    
    # Süreçleri tanımla
    p1 = Process(target=goru_sureci, args=(veri_kuyrugu,))
    p2 = Process(target=ucus_sureci, args=(veri_kuyrugu,))
    
    # Süreçleri aynı anda (paralel) başlat
    p1.start()
    p2.start()
    
    # İşlemlerin bitmesini bekle
    p1.join()
    p2.join()