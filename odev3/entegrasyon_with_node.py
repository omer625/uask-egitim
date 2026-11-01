import cv2
import numpy as np
import time
from multiprocessing import Process, Queue
from pymavlink import mavutil

# =========================================================================
# 1. DÜĞÜM (NODE): KAMERA (Yayıncı / Publisher)
# =========================================================================
class KameraNode(Process):
    def __init__(self, hedef_topic):
        super().__init__()
        self.publisher = hedef_topic # ROS'taki Publisher mantığı
        self.son_durum = None

    def run(self):
        print("[Kamera Node] Başlatıldı. Görüntü işleniyor...")
        cap = cv2.VideoCapture(2)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Kırmızı Tespit
            maske_kirmizi = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
            if cv2.countNonZero(maske_kirmizi) > 500:
                if self.son_durum != "ACIL_INIS":
                    print("[Kamera Node] Kırmızı Hedef! Topic'e ACIL_INIS yayınlanıyor (Publish).")
                    self.publisher.put("ACIL_INIS")
                    self.son_durum = "ACIL_INIS"
            
            # Mavi Tespit
            maske_mavi = cv2.inRange(hsv, np.array([90, 100, 100]), np.array([130, 255, 255]))
            konturlar, _ = cv2.findContours(maske_mavi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if konturlar and cv2.contourArea(max(konturlar, key=cv2.contourArea)) > 500:
                if self.son_durum != "KALKIS":
                    print("[Kamera Node] Mavi Hedef! Topic'e KALKIS yayınlanıyor (Publish).")
                    self.publisher.put("KALKIS")
                    self.son_durum = "KALKIS"

            cv2.imshow("Kamera Node Ekranı", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            
        cap.release()
        cv2.destroyAllWindows()


# =========================================================================
# 2. DÜĞÜM (NODE): UÇUŞ KONTROL (Abone / Subscriber)
# =========================================================================
class UcusNode(Process):
    def __init__(self, hedef_topic):
        super().__init__()
        self.subscriber = hedef_topic # ROS'taki Subscriber mantığı

    def run(self):
        print("[Uçuş Node] Başlatıldı. İHA'ya bağlanılıyor...")
        master = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
        master.wait_heartbeat()
        print("[Uçuş Node] Bağlantı başarılı! Topic dinleniyor (Subscribe).")
        
        durum = "YERDE"

        while True:
            # Topic'ten (Kuyruktan) mesaj var mı dinle
            if not self.subscriber.empty():
                mesaj = self.subscriber.get()
                
                if mesaj == "ACIL_INIS":
                    print("[Uçuş Node] ACİL İNİŞ mesajı alındı! RTL yapılıyor.")
                    master.set_mode(master.mode_mapping()['RTL'])
                    durum = "INIS"
                    
                elif mesaj == "KALKIS" and durum == "YERDE":
                    print("[Uçuş Node] KALKIS mesajı alındı! Görev icra ediliyor.")
                    master.set_mode(master.mode_mapping()['GUIDED'])
                    time.sleep(1)
                    master.arducopter_arm()
                    master.motors_armed_wait()
                    
                    master.mav.command_long_send(
                        master.target_system, master.target_component,
                        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
                        0, 0, 0, 0, 0, 0, 15
                    )
                    durum = "HAVADA"
                    
            time.sleep(0.1)


# =========================================================================
# ANA ÇALIŞTIRMA BLOKU (ROS2 Core Simülasyonu)
# =========================================================================
if __name__ == '__main__':
    print("--- UASK Pseudo-ROS Sistemi Başlatılıyor ---")
    
    # ROS'taki Topic (Mesajlaşma Kanalı) karşılığı: Queue
    komut_topic = Queue()
    
    # Node'ları oluştur ve aynı Topic'e (Kanala) bağla
    node_kamera = KameraNode(komut_topic)
    node_ucus = UcusNode(komut_topic)
    
    # Node'ları çalıştır
    node_kamera.start()
    node_ucus.start()
    
    node_kamera.join()
    node_ucus.join()