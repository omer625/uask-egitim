import cv2

# 0, bilgisayarın varsayılan kamerasını (webcam) temsil eder. 
# Not: Windows'ta kamera çok geç açılıyorsa 0 yerine cv2.CAP_DSHOW ekleyebilirsin: cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap = cv2.VideoCapture(0)

while True:
    # Kameradan anlık kareyi (frame) oku
    ret, frame = cap.read()
    
    # Eğer kameradan görüntü alınamazsa (kablo koptuysa vb.) döngüyü kır
    if not ret:
        print("Kameradan görüntü alınamadı!")
        break
        
    # Okunan kareyi ekranda göster
    cv2.imshow("UASK - Kamera Test", frame)
    
    # Klavyeden 'q' tuşuna basılırsa döngüden çık (1 milisaniyelik gecikme ile klavyeyi dinler)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kamera donanımını serbest bırak ve açık olan tüm OpenCV pencerelerini kapat
cap.release()
cv2.destroyAllWindows()