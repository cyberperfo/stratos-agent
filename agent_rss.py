import feedparser
import pandas as pd
import datetime
import time
import schedule
import os
from deep_translator import GoogleTranslator

# --- ÇEVİRİ MOTORU AYARLARI ---
translator = GoogleTranslator(source='auto', target='tr')

# --- İSTİHBARAT KAYNAKLARI ---
RSS_SOURCES = {
    "SavunmaSanayiST (TR)": "https://www.savunmasanayist.com/feed/",
    "AA Savunma (TR)": "https://www.aa.com.tr/tr/rss/default?cat=guncel",
    "Defence News (Global)": "https://www.defensenews.com/arc/outboundfeeds/rss/",
    "Air Force Times (USA)": "https://www.airforcetimes.com/arc/outboundfeeds/rss/",
    "Breaking Defense (Global)": "https://breakingdefense.com/feed/"
}

# --- KRİTİK KELİMELER (Hem Türkçe hem İngilizce) ---
# Yabancı kaynaklardaki kritik kelimeleri de yakalamak için İngilizcelerini ekledik.
KEYWORDS = [
    "füze", "ihracat", "imza", "teslimat", "sözleşme", "siha", "kaan", "bayraktar", # TR
    "missile", "deal", "contract", "uav", "drone", "export", "signed", "agreement" # ENG
]

def translate_if_needed(text, source_name):
    """Eğer kaynak Türkçe değilse, metni Türkçeye çevirir."""
    if "(TR)" in source_name:
        return text # Zaten Türkçe, dokunma.
    try:
        translated = translator.translate(text)
        return f"[ÇEVİRİ] {translated}" # Çevrildiğini belli et
    except:
        return text # Hata olursa orijinalini döndür

def scan_intelligence():
    print(f"\n📡 [TARAMA BAŞLADI] - {datetime.datetime.now().strftime('%H:%M:%S')}")
    all_news = []

    for source_name, url in RSS_SOURCES.items():
        try:
            print(f"   ↳ {source_name} taranıyor...", end="")
            feed = feedparser.parse(url)
            print(f" ✅ ({len(feed.entries)} başlık)")

            for entry in feed.entries[:3]: # Hız için her kaynaktan son 3 haberi al
                original_title = entry.title
                link = entry.link
                published = entry.published if 'published' in entry else "Tarih Yok"
                
                # 1. ÖNCELİK ANALİZİ (Global Tarama)
                priority = "Normal"
                for word in KEYWORDS:
                    if word in original_title.lower():
                        priority = "🔴 KRİTİK"
                        break
                
                # AA Filtresi
                if "AA" in source_name and priority == "Normal":
                    continue 

                # 2. DİL İŞLEME (Çeviri)
                # Sadece başlığı çevirip kaydedeceğiz
                final_title = translate_if_needed(original_title, source_name)

                all_news.append({
                    "Kaynak": source_name,
                    "Zaman": published,
                    "Öncelik": priority,
                    "Başlık": final_title, # Artık Türkçe!
                    "Orijinal Başlık": original_title, # Orijinali de saklayalım
                    "Link": link
                })

        except Exception as e:
            print(f" ❌ HATA: {e}")

    # --- RAPORLAMA ---
    if all_news:
        df = pd.DataFrame(all_news)
        file_name = "stratos_intel_db.csv"
        header_mod = not os.path.exists(file_name)
        
        try:
            df.to_csv(file_name, mode='a', index=False, encoding="utf-8-sig", header=header_mod)
            
            print("\n--- 🌍 KÜRESEL İSTİHBARAT RAPORU 🌍 ---")
            # Sadece kritik olanları göster
            kritik_df = df[df["Öncelik"] == "🔴 KRİTİK"]
            if not kritik_df.empty:
                # Ekrana Türkçe başlıkları bas
                print(kritik_df[["Kaynak", "Başlık"]].to_string(index=False))
            else:
                print("   (Kritik seviyede yeni gelişme yok, normal veriler kaydedildi.)")
            print("-" * 60)
            print(f"💾 [KAYIT] {len(df)} yeni veri veritabanına işlendi.\n")
            
        except Exception as e:
            print("Dosya hatası:", e)
    else:
        print("📭 Yeni veri bulunamadı.")

# --- ANA DÖNGÜ ---
print("==============================================")
print("   STRATOS v2.0 - ÇOK DİLLİ İSTİHBARAT AJANI")
print("==============================================")
scan_intelligence()

schedule.every(5).minutes.do(scan_intelligence)

while True:
    schedule.run_pending()
    time.sleep(1)