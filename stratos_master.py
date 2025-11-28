import feedparser
import google.generativeai as genai
import pandas as pd
import pymongo
import certifi
import schedule
import time
import datetime
import os

# ==========================================
# ⚙️ AYARLAR (BURALARI DOLDUR)
# ==========================================
API_KEY = "BURAYA_GOOGLE_API_KEYINI_YAPISTIR"
DB_USER = "admin"       # MongoDB Kullanıcı Adın
DB_PASS = "stratos2025" # MongoDB Şifren
CLUSTER = "cluster0.cglpxau.mongodb.net"

# Kaynaklar
RSS_SOURCES = {
    "SavunmaSanayiST": "https://www.savunmasanayist.com/feed/",
    "AA Savunma": "https://www.aa.com.tr/tr/rss/default?cat=guncel",
    "Defence News": "https://www.defensenews.com/arc/outboundfeeds/rss/",
    "Breaking Defense": "https://breakingdefense.com/feed/"
}

# Kritik Kelimeler
KEYWORDS = ["füze", "ihracat", "imza", "teslimat", "sözleşme", "missile", "deal", "contract", "uav", "siha", "kaan", "bayraktar", "aselsan", "roketsan"]

# ==========================================
# 🔌 BAĞLANTILARI KUR
# ==========================================
print("🔌 Sistem Başlatılıyor...")
MONGO_URI = f"mongodb+srv://{DB_USER}:{DB_PASS}@{CLUSTER}/?retryWrites=true&w=majority&appName=Cluster0"
genai.configure(api_key=API_KEY)

try:
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client["defenseDB"]
    collection = db["news_intel"]
    print("✅ Veritabanı Bağlantısı: AKTİF")
except Exception as e:
    print(f"❌ Veritabanı Hatası: {e}")
    exit()

# Model Seçimi
def get_model():
    try:
        return genai.GenerativeModel('gemini-2.0-flash')
    except:
        return genai.GenerativeModel('gemini-pro')
model = get_model()

# ==========================================
# 🕵️‍♂️ 1. GÖREV: İSTİHBARAT TOPLA (RSS)
# ==========================================
def collect_intelligence():
    print(f"\n📡 [TARAMA] Kaynaklar kontrol ediliyor... ({datetime.datetime.now().strftime('%H:%M')})")
    new_data = []
    
    for source, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]: # Her kaynaktan son 3 haber
                title = entry.title
                link = entry.link
                date = entry.published if 'published' in entry else datetime.datetime.now().strftime("%Y-%m-%d")
                
                # Öncelik Analizi
                priority = "Normal"
                for word in KEYWORDS:
                    if word in title.lower():
                        priority = "🔴 KRİTİK"
                        break
                
                if "AA" in source and priority == "Normal": continue

                # Veritabanında var mı diye kontrol et (Tekrarı önle)
                exists = collection.find_one({"title": title})
                if not exists and priority == "🔴 KRİTİK":
                    new_data.append({
                        "title": title,
                        "source": source,
                        "url": link,
                        "date": date,
                        "priority": priority,
                        "analysis": "", # Henüz analiz yok
                        "timestamp": datetime.datetime.now()
                    })
        except:
            continue
            
    if new_data:
        print(f"📥 {len(new_data)} yeni KRİTİK haber tespit edildi. Analize gönderiliyor...")
        analyze_intelligence(new_data) # Bulur bulmaz analize pasla
    else:
        print("📭 Yeni kritik gelişme yok. Nöbete devam.")

# ==========================================
# 🧠 2. GÖREV: ANALİZ ET VE YÜKLE (AI)
# ==========================================
def analyze_intelligence(news_list):
    print("🧠 [ANALİZ] Yapay Zeka devreye giriyor...")
    
    for item in news_list:
        print(f"   ↳ İşleniyor: {item['title'][:40]}...")
        
        prompt = f"""
        Sen STRATOS Savunma Stratejistisin.
        HABER: {item['title']}
        KAYNAK: {item['source']}
        
        Bana HTML formatında (sadece <p>, <ul>, <li>, <strong> kullanarak) şu analizi yap:
        1. Önem Derecesi (1-10)
        2. Stratejik Özet
        3. Türkiye'ye Etkisi (Tehdit/Fırsat)
        4. Mühendislik/Kariyer Tavsiyesi
        """
        
        try:
            response = model.generate_content(prompt)
            item['analysis'] = response.text.strip()
            
            # Veritabanına Kaydet
            collection.insert_one(item)
            print("      ✅ Buluta Yüklendi.")
            time.sleep(4) # API limiti için bekle
            
        except Exception as e:
            print(f"      ❌ Analiz Hatası: {e}")

# ==========================================
# 🔄 OTONOM DÖNGÜ
# ==========================================
print("=========================================")
print("   STRATOS OTONOM İSTİHBARAT SİSTEMİ")
print("   Durum: AKTİF | Kontrol Sıklığı: 5 Dk")
print("=========================================")

# İlk taramayı hemen yap
collect_intelligence()

# Sonra her 5 dakikada bir yap
schedule.every(5).minutes.do(collect_intelligence)

while True:
    schedule.run_pending()
    time.sleep(1)