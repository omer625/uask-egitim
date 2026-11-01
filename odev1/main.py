import cv2
import numpy as np

cap = cv2.VideoCapture(2)

# Logoyu döngüye girmeden önce saydamlık kanalıyla (Alpha) yükle ve boyutlandır
logo = cv2.imread('logo.png', cv2.IMREAD_UNCHANGED)
logo_boyut = 100
if logo is not None:
    logo = cv2.resize(logo, (logo_boyut, logo_boyut))

while True:
    ret, frame = cap.read()
    if not ret: break
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # =========================================================================
    # 1. KIRMIZI RENK VE ACİL ÇIKIŞ
    # =========================================================================
    maske_kirmizi = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
    if cv2.countNonZero(maske_kirmizi) > 500:
        print("KIRMIZI GÖRÜLDÜ! Acil Çıkış Yapılıyor...")
        break
        
    # =========================================================================
    # 2. MAVİ RENK, MERKEZ BULMA VE LOGO YERLEŞTİRME
    # =========================================================================
    alt_mavi = np.array([90, 100, 100])
    ust_mavi = np.array([130, 255, 255])
    maske_mavi = cv2.inRange(hsv, alt_mavi, ust_mavi)
    
    # Mavi alanların sınırlarını (konturlarını) bul
    konturlar, _ = cv2.findContours(maske_mavi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if konturlar:
        # Ekranda birden fazla mavi varsa en büyüğünü al
        en_buyuk = max(konturlar, key=cv2.contourArea)
        
        if cv2.contourArea(en_buyuk) > 500:
            # Merkezin X ve Y koordinatlarını matematiksel olarak bul
            M = cv2.moments(en_buyuk)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Logoyu ekrana yerleştirmek için sınırları belirle
                if logo is not None:
                    y1, y2 = cy - logo_boyut//2, cy + logo_boyut//2
                    x1, x2 = cx - logo_boyut//2, cx + logo_boyut//2
                    
                    # Logo ekranın dışına taşmıyorsa şeffaflığı koruyarak orijinal görüntüye bas
                    if y1 >= 0 and y2 <= frame.shape[0] and x1 >= 0 and x2 <= frame.shape[1]:
                        alpha_s = logo[:, :, 3] / 255.0
                        alpha_l = 1.0 - alpha_s
                        for c in range(0, 3):
                            frame[y1:y2, x1:x2, c] = (alpha_s * logo[:, :, c] + alpha_l * frame[y1:y2, x1:x2, c])
                else:
                    # Klasörde logo yoksa merkeze basit bir yeşil daire çiz
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

    # =========================================================================
    # 3. EKRAN ÇIKTILARI (3 PENCERE)
    # =========================================================================
    
    # Siyah arkaplanda sadece mavi objelerin kendi rengi görünsün
    renkli_maske = cv2.bitwise_and(frame, frame, mask=maske_mavi)
    
    cv2.imshow("1 - Orijinal Kamera (Logolu)", frame)
    cv2.imshow("2 - Siyah Beyaz Maske", maske_mavi)
    cv2.imshow("3 - Renkli Maskeleme", renkli_maske)
    cv2.imshow("4 - Kırmızı Maskeleme", maske_kirmizi)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()