import cv2
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QMessageBox, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap

# DNN model
MODEL_PATH = "models/frozen_inference_graph.pb"
CONFIG_PATH = "models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"

CLASS_LABELS = {
    44: 'şişe',
    47: 'bardak',
    48: 'çatal',
    49: 'bıçak',
    50: 'kaşık',
    52: 'muz',
    53: 'elma',
    59: 'pizza',
    60: 'donut',
    61: 'pasta',
    77: 'telefon',
}

PRODUCT_PRICES = {
    'şişe': 10,
    'çikolata': 5,
    'su': 3,
    'bardak': 2,
    'telefon': 15000
}

net = cv2.dnn.readNetFromTensorflow(MODEL_PATH, CONFIG_PATH)

def musteriden_bakiye_dus(musteri_id, urun, fiyat):
    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bakiye FROM musteriler WHERE id = ?", (musteri_id,))
    mevcut_bakiye = cursor.fetchone()

    if mevcut_bakiye is not None:
        yeni_bakiye = mevcut_bakiye[0] - fiyat
        cursor.execute("UPDATE musteriler SET bakiye = ? WHERE id = ?", (yeni_bakiye, musteri_id))
        conn.commit()
        QMessageBox.information(None, "Satış Tamamlandı", f"{urun} satın alındı. Yeni bakiye: {yeni_bakiye} TL")
    else:
        QMessageBox.critical(None, "Hata", "Müşteri bulunamadı!")
    conn.close()

class NesneTanimaDialog(QDialog):
    def __init__(self, musteri_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nesne Tanıma")
        self.setFixedSize(640, 500)
        self.musteri_id = musteri_id

        self.video_label = QLabel()
        self.status_label = QLabel("Durum: Bekleniyor...")

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)

        btn_kapat = QPushButton("Tanımayı Durdur")
        btn_kapat.clicked.connect(self.kapat)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_kapat)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)

        self.last_detected_item = None
        self.last_detection_time = datetime.min

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.status_label.setText("Kamera görüntüsü alınamadı.")
            return

        # CANLI GÖRÜNTÜ GÖSTER
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

        # NESNE ALGILAMA
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False)
        net.setInput(blob)
        detections = net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.3:
                class_id = int(detections[0, 0, i, 1])
                class_name = CLASS_LABELS.get(class_id, "Bilinmeyen")

                now = datetime.now()
                if (
                    class_name == self.last_detected_item and
                    now - self.last_detection_time < timedelta(seconds=3)
                ):
                    continue

                if class_name in PRODUCT_PRICES:
                    fiyat = PRODUCT_PRICES[class_name]
                    if self.musteri_id:
                        musteriden_bakiye_dus(self.musteri_id, class_name, fiyat)
                        self.status_label.setText(f"{class_name} algılandı. {fiyat} TL düşüldü.")
                        self.last_detected_item = class_name
                        self.last_detection_time = now
                    break

    def kapat(self):
        self.timer.stop()
        self.cap.release()
        self.close()
