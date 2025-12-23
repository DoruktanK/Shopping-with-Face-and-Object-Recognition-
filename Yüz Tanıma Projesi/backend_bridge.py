from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os
import sys
import sqlite3
# Backend fonksiyonları
from arayuz import (
    yuz_ve_nesne_tanima,
    yeni_musteri_ekle,
    musteri_sil,
    bakiye_guncelle_penceresi
)

from PyQt5.QtCore import pyqtSlot

class BackendBridge(QObject):
    @pyqtSlot(int)
    def deleteCustomer(self, musteri_id):
        print(f"🗑️ Müşteri siliniyor: ID {musteri_id}")
        try:
            conn = sqlite3.connect("musteriler.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM musteriler WHERE id = ?", (musteri_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Müşteri silme hatası: {e}")
 
                    
    @pyqtSlot(result='QVariant')
    def getAllCustomers(self):
     conn = sqlite3.connect("musteriler.db")
     cursor = conn.cursor()
     cursor.execute("SELECT id, isim, soyisim, bakiye FROM musteriler")
     rows = cursor.fetchall()
     conn.close()
     return [{"id": r[0], "isim": r[1], "soyisim": r[2], "bakiye": r[3]} for r in rows]

    @pyqtSlot(int, float)
    def updateCustomerBalance(self, musteri_id, yeni_bakiye):
     try:
        conn = sqlite3.connect("musteriler.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE musteriler SET bakiye = ? WHERE id = ?", (yeni_bakiye, musteri_id))
        conn.commit()
        conn.close()
        print(f"✅ Bakiye güncellendi: ID {musteri_id}, Yeni: {yeni_bakiye} TL")
     except Exception as e:
        print(f"❌ Bakiye güncelleme hatası: {e}")


    @pyqtSlot(str, str, str)
    def addCustomer(self, isim, soyisim, telefon):
        print(f"🟢 Yeni müşteri ekleniyor: {isim} {soyisim}, Tel: {telefon}")
        yeni_musteri_ekle(isim, soyisim, telefon)

    @pyqtSlot()
    def startRecognition(self):
        print("🟢 Yüz ve nesne tanıma başlatılıyor...")
        yuz_ve_nesne_tanima()
    
    @pyqtSlot(result='QVariant')
    def getCustomerList(self):
        """
        Veritabanındaki tüm müşteri bilgilerini döner.
        """
        import sqlite3
        conn = sqlite3.connect("musteriler.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, isim, soyisim, telefon FROM musteriler")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "isim": r[1], "soyisim": r[2], "telefon": r[3]} for r in rows]

         
    @pyqtSlot()
    def updateBalance(self):
        print("💰 Bakiye güncelleme penceresi açılıyor...")
        bakiye_guncelle_penceresi()

class WebUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yüz Tanıma Paneli")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()
        html_path = os.path.abspath("templates/index.html")
        self.browser.load(QUrl.fromLocalFile(html_path))

        self.channel = QWebChannel()
        self.backend = BackendBridge()
        self.channel.registerObject("backend", self.backend)
        self.browser.page().setWebChannel(self.channel)

        self.setCentralWidget(self.browser)
        

       
if __name__ == "__main__":
    from arayuz import yuz_tanimla  # ✅ En üste değil, burada içeri aktar

    app = QApplication(sys.argv)

    # ✅ Program başlarken yüz tanıma denemesi yapılır
    musteri_id = yuz_tanimla()
    if musteri_id:
        print(f"✅ Tanınan müşteri ID: {musteri_id}")

    window = WebUI()
    window.show()
    sys.exit(app.exec_())