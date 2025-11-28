import google.generativeai as genai
import sys

# --- ANAHTARINI BURAYA YAPIŞTIR ---
API_KEY = "AIzaSyAWvTSVn8V68-38uPaKQk8tqJH8aydYB5U" 
# ----------------------------------

print("📡 Bağlantı testi başlatılıyor...")

try:
    # 1. Anahtarı Ayarla
    genai.configure(api_key=API_KEY)
    
    # 2. Modelleri Listele (Bağlantı Kontrolü)
    print("🔑 Anahtar doğrulanıyor ve modeller aranıyor...")
    models = genai.list_models()
    
    available_models = []
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            
    if not available_models:
        print("❌ HATA: Anahtar doğru ama kullanılabilir model bulunamadı (Kütüphane güncellemesi gerekebilir).")
    else:
        print(f"✅ BAŞARILI! {len(available_models)} adet model bulundu.")
        print(f"   Bulunanlar: {available_models[:3]}...") # İlk 3 tanesini göster

        # 3. Zeka Testi (Cevap Üretme)
        print("\n🧠 Zeka testi yapılıyor (Model: gemini-1.5-flash)...")
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Bana 'Görev tamamlandı komutanım' yaz.")
            print(f"\n🤖 CEVAP: {response.text}")
            print("\n🎉 SİSTEM TAMAMEN ÇALIŞIYOR!")
        except Exception as e:
            print(f"\n⚠️ Flash modeli hata verdi, 'gemini-pro' deneniyor...")
            # Yedek model denemesi
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Görev tamam.")
            print(f"🤖 CEVAP (Yedek): {response.text}")

except Exception as e:
    print(f"\n❌ KRİTİK HATA: {e}")
    print("Lütfen anahtarı doğru yapıştırdığından emin ol.")