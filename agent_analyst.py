import google.generativeai as genai
import pandas as pd
import time
import os
import pymongo
import certifi
import datetime

# --- AYARLAR ---
API_KEY = "AIzaSyAWvTSVn8V68-38uPaKQk8tqJH8aydYB5U" 
# --- 1. AYARLAR ---
# DİKKAT: Kullanıcı adını MongoDB panelinden kopyaladığın gibi yapıştır!
# Önceki resimde "hypervisior" görünüyordu (fazladan 'i' var).
DB_USER = "admin"       # <-- Bunu değiştirdik
DB_PASS = "stratos2025" # <-- Bunu değiştirdik 
CLUSTER = "cluster0.cglpxau.mongodb.net" 

# Bağlantı Linki (Otomatik oluşur)
MONGO_URI = f"mongodb+srv://{DB_USER}:{DB_PASS}@{CLUSTER}/?retryWrites=true&w=majority&appName=Cluster0"
# Yapay Zeka Ayarı
genai.configure(api_key=API_KEY)

# MongoDB Bağlantısı
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["defenseDB"]
collection = db["news_intel"] # Yeni bir koleksiyon açıyoruz

# --- MODEL SEÇİCİ ---
def get_working_model():
    # ... (Model seçme kodu aynı kalacak, yer kaplamasın diye kısalttım) ...
    return genai.GenerativeModel('gemini-2.0-flash') 

model = get_working_model()

def analyze_and_upload():
    if not model: return

    print("\n🧠 [STRATOS ANALİST] Veritabanına Bağlanıyor...")
    
    # 1. CSV'den Ham Verileri Oku (agent_rss.py'nin ürettikleri)
    try:
        df = pd.read_csv("stratos_intel_db.csv", on_bad_lines='skip', engine='python')
    except FileNotFoundError:
        print("❌ CSV dosyası bulunamadı.")
        return

    # 'Analiz' sütunu yoksa oluştur
    if "Analiz" not in df.columns: df["Analiz"] = ""

    # 2. Analiz Edilmemiş Kritik Haberleri Bul
    pending_news = df[(df["Öncelik"] == "🔴 KRİTİK") & (df["Analiz"].isna() | (df["Analiz"] == ""))]

    if pending_news.empty:
        print("✅ Analiz edilecek yeni veri yok. Sistem güncel.")
        return

    print(f"🔍 {len(pending_news)} adet yeni istihbarat analiz ediliyor...\n")

    for index, row in pending_news.iterrows():
        baslik = row["Başlık"]
        kaynak = row["Kaynak"]
        link = row["Link"]
        tarih = row["Zaman"]
        
        print(f"   Düşünülüyor... -> {baslik[:40]}...")

        prompt = f"""
        Sen STRATOS Savunma Stratejistisin.
        HABER: {baslik}
        KAYNAK: {kaynak}
        
        Bana HTML formatında (sadece <p>, <ul>, <li>, <strong> kullanarak) şu analizi yap:
        1. Önem Derecesi (1-10)
        2. Stratejik Özet
        3. Türkiye'ye Etkisi (Tehdit/Fırsat)
        4. Mühendislik/Kariyer Tavsiyesi
        """

        try:
            response = model.generate_content(prompt)
            analiz_sonucu = response.text.strip()
            
            # CSV'ye kaydet (Yedek)
            df.at[index, "Analiz"] = analiz_sonucu
            
            # --- MONGODB'YE GÖNDER (CANLI YAYIN) ---
            intel_document = {
                "title": baslik,
                "source": kaynak,
                "url": link,
                "date": tarih or datetime.datetime.now().strftime("%Y-%m-%d"),
                "priority": "CRITICAL",
                "analysis": analiz_sonucu, # AI Raporu
                "timestamp": datetime.datetime.now()
            }
            
            # Aynı haber varsa tekrar ekleme (upsert)
            collection.update_one(
                {"title": baslik}, 
                {"$set": intel_document}, 
                upsert=True
            )
            
            print(f"✅ Analiz Buluta Yüklendi: {baslik[:30]}...")
            time.sleep(4)

        except Exception as e:
            print(f"❌ Hata: {e}")

    # CSV'yi de güncelle
    df.to_csv("stratos_intel_db.csv", index=False, encoding="utf-8-sig")
    print("\n💾 Tüm işlemler tamamlandı.")

if __name__ == "__main__":
    analyze_and_upload()