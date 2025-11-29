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
        "title": "🔴 OPERASYONEL TEST: STRATOS AKTİF VE ÇALIŞIYOR",
        "source": "STRATOS KOMUTA MERKEZİ",
        "url": "#",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "priority": "CRITICAL",
        "analysis": """
        <p><strong>DURUM RAPORU:</strong></p>
        <ul>
            <li>Bu mesajı web sitesinde görüyorsanız, <strong>Python Ajanı, Veritabanı ve Web Sitesi</strong> arasındaki tüm hatlar %100 çalışıyor demektir.</li>
            <li>Şu an gerçek bir haber akışı olmadığı için bu test mesajı gönderilmiştir.</li>
        </ul>
        <p><strong>SONUÇ:</strong> Sistem otonom nöbet modundadır.</p>
        """,
        "timestamp": datetime.datetime.now()
    }
    
    # Veriyi Zorla Yaz
    collection.insert_one(test_intel)
    print("✅ TEST VERİSİ BULUTA BAŞARIYLA GÖNDERİLDİ!")
    print("👉 Şimdi siteye gidip F5 yapabilirsin.")

except Exception as e:
    print(f"❌ HATA: {e}")