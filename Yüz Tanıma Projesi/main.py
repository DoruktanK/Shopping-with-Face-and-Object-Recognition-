import cv2
import face_recognition

# Kamera indeksini belirleyin
camera_index = 1
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print(f"Kamera {camera_index} açılamadı!")
    exit()

print(f"Kamera {camera_index} başarıyla açıldı!")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kamera verisi alınamadı!")
        break

    # OpenCV BGR formatında çalışır, face_recognition RGB ister
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Yüzleri algıla
    face_locations = face_recognition.face_locations(rgb_frame)

    # Algılanan yüzlerin etrafına dikdörtgen çiz
    for top, right, bottom, left in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Görüntüyü göster
    cv2.imshow("Yüz Tanıma", frame)

    # 'q' tuşuna basarak çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
