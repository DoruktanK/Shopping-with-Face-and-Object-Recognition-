import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect("musteriler.db")
cursor = conn.cursor()

# musteriler tablosuna bakiye sütunu ekle
try:
    cursor.execute("ALTER TABLE musteriler ADD COLUMN bakiye REAL DEFAULT 100.0")
    print("Bakiye sütunu başarıyla eklendi ve başlangıç bakiyesi 100.0 olarak atandı.")
except sqlite3.OperationalError:
    print("Bakiye sütunu zaten mevcut.")

# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()
