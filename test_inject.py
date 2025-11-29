import pymongo
import certifi
import datetime

# --- AYARLAR ---
DB_USER = "admin"
DB_PASS = "stratos2025"
CLUSTER = "cluster0.cglpxau.mongodb.net"

MONGO_URI = f"mongodb+srv://{DB_USER}:{DB_PASS}@{CLUSTER}/?retryWrites=true&w=majority&appName=Cluster0"

try:
    print("🔌 Veritabanına bağlanılıyor...")
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client["defenseDB"]
    collection = db["news_intel"]
    
    # --- SAHTE İSTİHBARAT VERİSİ ---
    test_intel = {
        "title": "🔴 SİSTEM TESTİ: STRATOS BAĞLANTISI BAŞARILI",
        "source": "STRATOS KOMUTA MERKEZİ",
        "url": "https://www.google.com",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "priority": "CRITICAL",
        "analysis": """
        <p><strong>DURUM ANALİZİ:</strong></p>
        <ul>
            <li>Bu mesajı görüyorsanız, Python ajanı ve MongoDB arasındaki veri hattı <strong>kusursuz çalışıyor</strong> demektir.</li>
            <li>Web sitesi (Frontend) veriyi başarıyla çekmiştir.</li>
        </ul>
        <p><strong>SONUÇ:</strong> Operasyonel kurulum tamamlanmıştır.</p>
        """,
        "timestamp": datetime.datetime.now()
    }
    
    # Veriyi Zorla Yaz
    collection.insert_one(test_intel)
    print("✅ TEST VERİSİ BULUTA YÜKLENDİ!")
    print("👉 Şimdi web sitesini yenile (F5) ve sağ tarafa bak.")

except Exception as e:
    print(f"❌ HATA: {e}")