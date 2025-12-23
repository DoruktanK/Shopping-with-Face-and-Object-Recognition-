import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# Şekil ve eksen oluştur
fig, ax = plt.subplots(figsize=(8, 6))

# İşlem adımları
steps = [
    "Başlat",
    "Kamera Açılır",
    "Yüz Tanıma",
    "Müşteri Bilgileri Veritabanından Çekilir",
    "Nesne Tanıma",
    "Ürün ve Fiyat Bilgileri Gösterilir",
    "Bakiye Güncellenir",
    "İşlem Tamamlandı"
]

# Her adıma x ve y koordinatları veriyoruz
coords = [
    (0.5, 0.9),
    (0.5, 0.8),
    (0.5, 0.7),
    (0.5, 0.6),
    (0.5, 0.5),
    (0.5, 0.4),
    (0.5, 0.3),
    (0.5, 0.2)
]

# Adımları çizin
for i, (x, y) in enumerate(coords):
    ax.text(x, y, steps[i], fontsize=12, ha="center", bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="#FFA07A"))

# Oklarla adımları bağlayın
for i in range(len(coords) - 1):
    arrow = FancyArrowPatch(coords[i], coords[i + 1], connectionstyle="arc3,rad=0.1",
                            arrowstyle="->", mutation_scale=20, color="black")
    ax.add_patch(arrow)

# Eksenleri kapat ve düzenle
ax.axis("off")
plt.title("İşlem Akış Diyagramı", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.show()
