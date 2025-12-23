from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys
import os
from arayuz import (
    yuz_tanimla,
    nesne_tanima,
    fatura_goster
)


def yuz_ve_nesne_tanima():
    """
    Yüz ve Nesne Tanıma işlemlerini birlikte başlatır.
    """
    musteri_id = yuz_tanimla()
    
    if musteri_id:
        urun_adi, fiyat = nesne_tanima(musteri_id)
        
        if urun_adi and fiyat:
            fatura_goster(musteri_id, urun_adi, fiyat)
        else:
            from tkinter import messagebox
            messagebox.showinfo("Bilgi", "Nesne tanımlanamadı.")
    else:
        from tkinter import messagebox
        messagebox.showerror("Hata", "Müşteri tanınamadı, nesne tanıma başlatılamadı!")



class WebUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yüz Tanıma - CoreUI Arayüz")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()
        path = os.path.abspath("templates/index.html")
        self.browser.load(QUrl.fromLocalFile(path))
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebUI()
    window.show()
    sys.exit(app.exec_())
