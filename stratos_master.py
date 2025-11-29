import feedparser
import google.generativeai as genai
import pandas as pd
import pymongo
import certifi
import schedule
import time
import datetime
import os
from flask import Flask # YENİ: Sahte sunucu için
import threading # YENİ: Aynı anda hem sunucu hem ajan çalışsın diye
from dotenv import load_dotenv # YENİ: Kasa okuyucu

# ==========================================
# ⚙️ AYARLAR (BURALARI KENDİ BİLGİLERİNLE DOLDUR)
# ==========================================
API_KEY = os.environ.get("GOOGLE_API_KEY") 

# MongoDB bilgilerini de Render'dan çekecek şekilde ayarlayalım (Güvenli)
# Eğer Render'daysa oradaki ayarları, değilse buradakileri kullanır
DB_USER = os.environ.get("DB_USER", "admin")       
DB_PASS = os.environ.get("DB_PASS", "stratos2025") 
CLUSTER = "cluster0.cglpxau.mongodb.net"

# ==========================================
# 🌐 SAHTE WEB SUNUCUSU (RENDER İÇİN MASKE)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "STRATOS İSTİHBARAT AJANI AKTİF VE NÖBETTE! 🦅"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

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

# Model Seçimi
def get_model():
    try:
        return genai.GenerativeModel('gemini-2.0-flash')
    except:
        return genai.GenerativeModel('gemini-pro')
model = get_model()

# Kaynaklar ve Kelimeler
RSS_SOURCES = {
    "SavunmaSanayiST": "https://www.savunmasanayist.com/feed/",
    "AA Savunma": "https://www.aa.com.tr/tr/rss/default?cat=guncel",
    "Defence News": "https://www.defensenews.com/arc/outboundfeeds/rss/",
    "Breaking Defense": "https://breakingdefense.com/feed/"
}
# --- STRATEJİK FİLTRE (Gürültüyü engeller, istihbaratı yakalar) ---
KEYWORDS = [
    # Türkçe Kritik Terimler
    "füze", "ihracat", "imza", "teslimat", "sözleşme", "anlaşma", 
    "uav", "siha", "iha", "dron", "savaş uçağı", "helikopter", "tank", 
    "donanma", "denizaltı", "radar", "elektronik harp", "siber",
    "kaan", "kızılelma", "hürjet", "atak", "bayraktar", "akıncı", "aksungur",
    "aselsan", "roketsan", "tusaş", "havelsan", "stm", "baykar", "bmc",
    
    # İngilizce Kritik Terimler (Global Kaynaklar İçin)
    "missile", "export", "signed", "deal", "contract", "agreement", "delivery",
    "fighter jet", "helicopter", "navy", "submarine", "army", "air force",
    "lockheed", "boeing", "northrop", "airbus", "rheinmetall", "saab"
]

# ... (BURADAKİ FONKSİYONLAR AYNI KALIYOR: collect_intelligence, analyze_intelligence) ...
# Kod uzamasın diye fonksiyonları tekrar yazmıyorum, senin mevcut kodundaki gibi kalsın.
# Sadece en alt kısmı değiştiriyoruz:

# ==========================================
# 🕵️‍♂️ İŞ FONKSİYONLARI (KOPYALA YAPIŞTIR YAPTIYSAN BURAYA DİKKAT)
# ==========================================
def collect_intelligence():
    print(f"\n📡 [TARAMA] ({datetime.datetime.now().strftime('%H:%M')})")
    new_data = []
    for source, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                title = entry.title
                link = entry.link
                date = entry.published if 'published' in entry else datetime.datetime.now().strftime("%Y-%m-%d")
                priority = "Normal"
                for word in KEYWORDS:
                    if word in title.lower():
                        priority = "🔴 KRİTİK"
                        break
                if "AA" in source and priority == "Normal": continue
                
                exists = collection.find_one({"title": title})
                if not exists and priority == "🔴 KRİTİK":
                    new_data.append({"title": title, "source": source, "url": link, "date": date, "priority": priority, "analysis": "", "timestamp": datetime.datetime.now()})
        except: continue
            
    if new_data:
        print(f"📥 {len(new_data)} yeni haber. Analiz başlıyor...")
        analyze_intelligence(new_data)
    else:
        print("📭 Yeni gelişme yok.")

def analyze_intelligence(news_list):
    for item in news_list:
        print(f"   ↳ İşleniyor: {item['title'][:30]}...")
        prompt = f"Sen STRATOS Savunma Stratejistisin. HABER: {item['title']} KAYNAK: {item['source']}. Bana HTML formatında (sadece p, ul, li, strong) analiz yap: 1.Önem(1-10) 2.Özet 3.Etki 4.Kariyer"
        try:
            response = model.generate_content(prompt)
            item['analysis'] = response.text.strip()
            collection.insert_one(item)
            print("      ✅ Buluta Yüklendi.")
            time.sleep(4)
        except Exception as e: print(f"❌ Hata: {e}")

# ==========================================
# 🔄 OTONOM DÖNGÜ VE SUNUCU BAŞLATMA (BURASI ÇOK ÖNEMLİ)
# ==========================================
if __name__ == "__main__":
    # 1. Önce Sahte Web Sunucusunu Arka Planda Başlat (Render'ı kandırmak için)
    t = threading.Thread(target=run_web_server)
    t.start()

    # 2. Sonra Ajanı Başlat
    print("=========================================")
    print("   STRATOS OTONOM İSTİHBARAT SİSTEMİ")
    print("=========================================")
    
    collect_intelligence() # İlk tarama
    schedule.every(10).minutes.do(collect_intelligence)

    while True:
        schedule.run_pending()
        time.sleep(1)