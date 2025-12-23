import os
import cv2
import face_recognition
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from nesnetanima import NesneTanimaDialog

from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QMainWindow,
    QApplication
)

import time
import threading
from nesnetanima import NesneTanimaDialog

def yuz_ve_nesne_tanima():
    musteri_id = yuz_tanimla()
    if musteri_id:
        print(f"✅ Tanınan müşteri ID: {musteri_id}")
        from nesnetanima import NesneTanimaDialog
        dialog = NesneTanimaDialog(musteri_id)
        dialog.exec_()
    else:
        print("❌ Müşteri bulunamadı!")





def veritabanindan_bilgileri_getir(foto_yolu):
    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM musteriler WHERE yuz_fotografi = ?", (foto_yolu,))
    sonuc = cursor.fetchone()
    conn.close()
    return sonuc



def bilgileri_goster(kullanici_bilgileri):
    pencere = QDialog()
    pencere.setWindowTitle("Müşteri Bilgileri")
    pencere.resize(400, 300)

    layout = QVBoxLayout()
    layout.addWidget(QLabel(f"İsim: {kullanici_bilgileri[1]}"))
    layout.addWidget(QLabel(f"Soyisim: {kullanici_bilgileri[2]}"))
    layout.addWidget(QLabel(f"Telefon: {kullanici_bilgileri[3]}"))
    layout.addWidget(QLabel(f"Bakiye: {kullanici_bilgileri[5]} TL"))
    layout.addWidget(QLabel(f"Fotoğraf Yolu: {kullanici_bilgileri[4]}"))

    kapat_btn = QPushButton("Kapat")
    kapat_btn.clicked.connect(pencere.close)
    layout.addWidget(kapat_btn)

    pencere.setLayout(layout)
    pencere.exec_()



def yuz_tanimla():
    # Yüz fotoğraflarını ve müşteri ID’lerini yükle
    known_encodings = []
    musteri_ids = []

    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, yuz_fotografi FROM musteriler")
    for row in cursor.fetchall():
        musteri_id, foto_path = row
        if os.path.exists(foto_path):
            img = face_recognition.load_image_file(foto_path)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                known_encodings.append(encodings[0])
                musteri_ids.append(musteri_id)
    conn.close()

    # Kamera açılır
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera açılamadı!")
        return None

    print("📷 Kamera açıldı. Yüz taraması başlatılıyor...")
    for _ in range(20):  # Kamera başlatma gecikmesi
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Görüntü alınamadı.")
        return None

    # Tanınacak yüzü kodla
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb_frame)
    encodings = face_recognition.face_encodings(rgb_frame, faces)

    for face_encoding in encodings:
        # Karşılaştırma ve mesafe kontrolü
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        if len(face_distances) == 0:
            break

        best_match_index = np.argmin(face_distances)
        if face_distances[best_match_index] < 0.45:  # Daha sıkı eşik
            matched_id = musteri_ids[best_match_index]
            return matched_id

    # Eğer hiçbiri tanınmadıysa uyarı ver
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Yüz Tanınamadı")
    msg.setText("📛 Bu kişi sistemde kayıtlı değil. Lütfen müşteri olarak kaydedin.")
    msg.exec_()

    return None




def fatura_goster(musteri_id, urun_adi, fiyat):
    import sqlite3
    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT isim, soyisim, bakiye FROM musteriler WHERE id = ?", (musteri_id,))
    musteri_bilgileri = cursor.fetchone()
    conn.close()

    if not musteri_bilgileri:
        QMessageBox.critical(None, "Hata", "Müşteri bilgileri alınamadı!")
        return

    isim, soyisim, bakiye = musteri_bilgileri

    pencere = QWidget()
    pencere.setWindowTitle("Fatura")
    pencere.setFixedSize(400, 300)

    layout = QVBoxLayout()
    layout.addWidget(QLabel(f"İsim: {isim} {soyisim}"))
    layout.addWidget(QLabel(f"Bakiye: {bakiye} TL"))
    layout.addWidget(QLabel(f"Ürün: {urun_adi}"))
    layout.addWidget(QLabel(f"Fiyat: {fiyat} TL"))

    onayla_buton = QPushButton("Onayla")
    onayla_buton.clicked.connect(lambda: bakiye_dusecek(musteri_id, urun_adi, fiyat))
    layout.addWidget(onayla_buton)

    pencere.setLayout(layout)
    pencere.show()






def bakiye_dusecek(musteri_id, urun, fiyat):
    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bakiye FROM musteriler WHERE id = ?", (musteri_id,))
    mevcut = cursor.fetchone()

    if mevcut:
        yeni_bakiye = mevcut[0] - fiyat
        cursor.execute("UPDATE musteriler SET bakiye = ? WHERE id = ?", (yeni_bakiye, musteri_id))
        conn.commit()
        QMessageBox.information(None, "Satın Alındı", f"{urun} satın alındı. Yeni bakiye: {yeni_bakiye} TL")
    else:
        QMessageBox.critical(None, "Hata", "Müşteri bulunamadı!")
    conn.close()



def yeni_musteri_ekle(isim, soyisim, telefon):
    """
    Kamera ile yüz fotoğrafı çekerek veritabanına yeni müşteri ekler.
    """
    bakiye = 100.0  # Varsayılan bakiye

    if not isim or not soyisim or not telefon:
        QMessageBox.critical(None, "Hata", "Tüm alanları doldurun!")
        return

    if not os.path.exists("yuz_fotograflari"):
        os.makedirs("yuz_fotograflari")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        QMessageBox.critical(None, "Hata", "Kamera açılamadı!")
        return

    ret, frame = cap.read()
    if ret:
        dosya_adi = f"yuz_fotograflari/musteri_{isim}_{soyisim}.jpg"
        cv2.imwrite(dosya_adi, frame)
        cap.release()
        try:
            cv2.destroyAllWindows()
        except:
            pass

        try:
            conn = sqlite3.connect("musteriler.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO musteriler (isim, soyisim, telefon, yuz_fotografi, bakiye)
                VALUES (?, ?, ?, ?, ?)
            """, (isim, soyisim, telefon, dosya_adi, bakiye))
            conn.commit()
            conn.close()
            QMessageBox.information(None, "Başarılı", f"{isim} {soyisim} eklendi.")
        except Exception as e:
            QMessageBox.critical(None, "Veritabanı Hatası", f"Hata: {e}")
    else:
        QMessageBox.critical(None, "Hata", "Fotoğraf alınamadı!")
        cap.release()
        try:
            cv2.destroyAllWindows()
        except:
            pass


def musteri_sil():
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QDialog

    dialog = QDialog()
    dialog.setWindowTitle("Müşteri Sil")
    layout = QVBoxLayout()

    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, isim, soyisim, bakiye FROM musteriler")
    musteriler = cursor.fetchall()
    conn.close()

    for musteri in musteriler:
        musteri_id, isim, soyisim, bakiye = musteri
        btn = QPushButton(f"{isim} {soyisim} - {bakiye} TL")
        btn.clicked.connect(lambda _, mid=musteri_id: musteri_sil_buton(mid, dialog))
        layout.addWidget(btn)

    scroll = QScrollArea()
    container = QWidget()
    container.setLayout(layout)
    scroll.setWidget(container)
    scroll.setWidgetResizable(True)

    scroll_layout = QVBoxLayout()
    scroll_layout.addWidget(scroll)
    dialog.setLayout(scroll_layout)
    dialog.exec_()



def bakiye_guncelle_penceresi():
    pencere = QDialog()
    pencere.setWindowTitle("Bakiye Güncelle")
    layout = QVBoxLayout()

    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, isim, soyisim, bakiye FROM musteriler")
    musteriler = cursor.fetchall()
    conn.close()

    for musteri in musteriler:
        musteri_id, isim, soyisim, bakiye = musteri
        row = QWidget()
        row_layout = QHBoxLayout()
        label = QLabel(f"{isim} {soyisim} - Bakiye: {bakiye} TL")
        guncelle_btn = QPushButton("Güncelle")
        guncelle_btn.clicked.connect(lambda checked, mid=musteri_id: bakiye_guncelleme_formu(mid))
        row_layout.addWidget(label)
        row_layout.addWidget(guncelle_btn)
        row.setLayout(row_layout)
        layout.addWidget(row)

    kapat_btn = QPushButton("Kapat")
    kapat_btn.clicked.connect(pencere.close)
    layout.addWidget(kapat_btn)
    pencere.setLayout(layout)
    pencere.exec_()



def bakiye_guncelleme_formu(musteri_id):
    pencere = QDialog()
    pencere.setWindowTitle("Bakiye Güncelleme")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Yeni Bakiye Girin:"))
    yeni_bakiye_input = QLineEdit()
    layout.addWidget(yeni_bakiye_input)

    def guncelle():
        try:
            yeni_bakiye = float(yeni_bakiye_input.text())
            conn = sqlite3.connect("musteriler.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE musteriler SET bakiye = ? WHERE id = ?", (yeni_bakiye, musteri_id))
            conn.commit()
            conn.close()
            QMessageBox.information(None, "Başarılı", "Bakiye güncellendi!")
            pencere.close()
        except ValueError:
            QMessageBox.critical(None, "Hata", "Geçerli bir sayı giriniz!")

    guncelle_btn = QPushButton("Güncelle")
    guncelle_btn.clicked.connect(guncelle)
    layout.addWidget(guncelle_btn)

    pencere.setLayout(layout)
    pencere.exec_()



def musteri_sil_buton(musteri_id, dialog):
    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM musteriler WHERE id = ?", (musteri_id,))
    conn.commit()
    conn.close()

    from PyQt5.QtWidgets import QMessageBox, QWidget
    QMessageBox.information(QWidget(), "Başarılı", f"Müşteri ID {musteri_id} silindi.")
    dialog.accept()
    musteri_sil()




def musteriden_bakiye_dus(musteri_id, urun, fiyat):
  
    

    conn = sqlite3.connect("musteriler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bakiye FROM musteriler WHERE id = ?", (musteri_id,))
    mevcut_bakiye = cursor.fetchone()

    if mevcut_bakiye:
        yeni_bakiye = mevcut_bakiye[0] - fiyat
        cursor.execute("UPDATE musteriler SET bakiye = ? WHERE id = ?", (yeni_bakiye, musteri_id))
        conn.commit()
        QMessageBox.information(None, "Satış Tamamlandı", f"{urun} satın alındı. Yeni bakiye: {yeni_bakiye} TL")
    else:
        QMessageBox.critical(None, "Hata", "Müşteri bulunamadı!")

    conn.close()

    def fatura_penceresi_goster(musteri_id, urun_adi, fiyat):
   
    
        conn = sqlite3.connect("musteriler.db")
        cursor = conn.cursor()
        cursor.execute("SELECT isim, soyisim, bakiye FROM musteriler WHERE id = ?", (musteri_id,))
        musteri_bilgileri = cursor.fetchone()
        conn.close()

        if musteri_bilgileri:
         isim, soyisim, bakiye = musteri_bilgileri
         fatura_pencere = tk.Toplevel()
        fatura_pencere.title("Fatura")
        fatura_pencere.geometry("400x300")

        tk.Label(fatura_pencere, text=f"İsim: {isim} {soyisim}", font=("Arial", 12)).pack(pady=10)
        tk.Label(fatura_pencere, text=f"Bakiye: {bakiye} TL", font=("Arial", 12)).pack(pady=10)
        tk.Label(fatura_pencere, text=f"Ürün: {urun_adi}", font=("Arial", 12)).pack(pady=10)
        tk.Label(fatura_pencere, text=f"Fiyat: {fiyat} TL", font=("Arial", 12)).pack(pady=10)

        # Onayla butonu
        tk.Button(fatura_pencere, text="Onayla", command=lambda: bakiye_dusecek(musteri_id, urun_adi, fiyat)).pack(pady=20)

        fatura_pencere.mainloop()



from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
import sqlite3

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
    61: 'pasta'
}

PRODUCT_PRICES = {
    'şişe': 10,
    'çikolata': 5,
    'su': 3,
    'bardak': 2
}

class NesneTanimaDialog(QDialog):
    def __init__(self, musteri_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nesne Tanıma")
        self.setFixedSize(640, 500)
        self.musteri_id = musteri_id

        # OpenCV modeli
        self.net = cv2.dnn.readNetFromTensorflow("models/frozen_inference_graph.pb", "models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt")

        self.label = QLabel("Kamera başlatılıyor...")
        self.label.setFixedSize(640, 480)

        self.kapat_btn = QPushButton("İptal")
        self.kapat_btn.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.kapat_btn)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.label.setText("Kamera alınamadı")
            return

        # Nesne tanıma
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False)
        self.net.setInput(blob)
        detections = self.net.forward()

        detected = False
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.3:
                class_id = int(detections[0, 0, i, 1])
                class_name = CLASS_LABELS.get(class_id, "bilinmeyen")

                if class_name in PRODUCT_PRICES:
                    fiyat = PRODUCT_PRICES[class_name]
                    self.timer.stop()
                    self.cap.release()
                    self.kamera_goster(QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888))
                    self.fiyati_dusur_ve_goster(class_name, fiyat)
                    self.accept()
                    detected = True
                    break

        if not detected:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qimg))

    def fiyati_dusur_ve_goster(self, urun, fiyat):
        conn = sqlite3.connect("musteriler.db")
        cursor = conn.cursor()
        cursor.execute("SELECT bakiye FROM musteriler WHERE id = ?", (self.musteri_id,))
        mevcut = cursor.fetchone()
        if mevcut:
            yeni = mevcut[0] - fiyat
            cursor.execute("UPDATE musteriler SET bakiye = ? WHERE id = ?", (yeni, self.musteri_id))
            conn.commit()
            QMessageBox.information(self, "Satış Tamamlandı", f"{urun} ({fiyat} TL) tanındı.\nYeni bakiye: {yeni} TL")
        else:
            QMessageBox.warning(self, "Hata", "Müşteri bulunamadı!")
        conn.close()

    def kamera_goster(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        event.accept()
