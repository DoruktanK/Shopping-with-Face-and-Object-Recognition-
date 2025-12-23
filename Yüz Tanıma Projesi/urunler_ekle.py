import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect("musteriler.db")
cursor = conn.cursor()

# Ürünler tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS urunler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    urun_adi TEXT NOT NULL,
    fiyat REAL NOT NULL
)
""")

# Örnek ürünler ekle
urunler = [
    ("Su", 5.0),
    ("Çikolata", 10.0),
    ("Cips", 15.0),
    ("Kola", 8.0),
    ("Telefon", 100.0) 
]

cursor.executemany("INSERT INTO urunler (urun_adi, fiyat) VALUES (?, ?)", urunler)

# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()

print("Ürünler başarıyla eklendi.")
