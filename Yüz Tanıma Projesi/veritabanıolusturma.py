import sqlite3

# Veritabanını bağlayın
conn = sqlite3.connect("musteriler.db")
cursor = conn.cursor()

# Kayıtları kontrol edin
cursor.execute("SELECT * FROM musteriler")
kayitlar = cursor.fetchall()

for kayit in kayitlar:
    print(kayit)

conn.close()
