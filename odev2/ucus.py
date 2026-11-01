from pymavlink import mavutil
import time

def baglan(port='tcp:127.0.0.1:5762'):
    """SITL simülasyonuna bağlanır, heartbeat bekler ve telemetri akışını başlatır."""
    print(f"{port} adresine bağlanılıyor...")
    master = mavutil.mavlink_connection(port)
    master.wait_heartbeat()
    print("Bağlantı başarılı! İHA ile iletişim kuruldu.")
    
    # Saniyede 2 kez telemetri verisi (irtifa vb.) iste
    master.mav.request_data_stream_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 
        2, 1
    )
    return master

def mod_degistir(master, mod_adi):
    """İHA'nın uçuş modunu değiştirir (Örn: GUIDED, RTL, STABILIZE)."""
    print(f"Uçuş modu {mod_adi} olarak ayarlanıyor...")
    mod_id = master.mode_mapping()[mod_adi]
    master.set_mode(mod_id)
    time.sleep(1) # Modun oturması için ufak bir pay

def arm_et(master):
    """Pervaneleri çalıştırır (ARM)."""
    print("İHA ARM ediliyor...")
    master.arducopter_arm()
    master.motors_armed_wait() # ARM olana kadar kodu burada bekletir
    print("İHA başarıyla ARM edildi!")

def kalkis(master, hedef_irtifa):
    """Belirtilen irtifaya kalkış yapar ve ulaşana kadar kodu bekletir."""
    print(f"{hedef_irtifa} metreye kalkış (Takeoff) başlatıldı...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, hedef_irtifa
    )
    
    # Hedef irtifaya çıkana kadar bekle ve terminale yazdır
    while True:
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        if msg:
            anlik_irtifa = msg.relative_alt / 1000.0
            print(f"Anlık İrtifa: {anlik_irtifa:.2f} metre")
            
            # Hedefin %95'ine ulaşıldığında kalkış tamamlanmış sayılır
            if anlik_irtifa >= hedef_irtifa * 0.95:
                print("Hedef irtifaya ulaşıldı!")
                break

def rtl(master):
    """Kalktığı noktaya otomatik iniş (Return to Launch) yapar."""
    print("RTL (Acil İniş) başlatılıyor...")
    mod_degistir(master, 'RTL')


# Eğer bu dosya doğrudan çalıştırılırsa (başka bir koda import edilmediyse) aşağıdaki test senaryosunu işlet
if __name__ == '__main__':
    # 1. Simülasyona bağlan
    iha = baglan()
    
    # 2. Kod ile kontrol edebilmek için GUIDED moduna al
    mod_degistir(iha, 'GUIDED')
    
    # 3. Motorları çalıştır
    arm_et(iha)
    
    # 4. 15 Metreye kalk
    kalkis(iha, 15)
    
    # 5. Başarıyı görmek için havada 5 saniye bekle
    print("Havada 5 saniye hover (asılı kalma) yapılıyor...")
    time.sleep(5)
    
    # 6. Güvenli bir şekilde kalktığı yere in
    rtl(iha)
    print("Görev tamamlandı. Otonom iniş izleniyor.")