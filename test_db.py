import pymongo
import certifi

# --- YENİ KİMLİK KARTLARI ---
# Kullanıcı adı: admin
# Şifre: stratos2025
uri = "mongodb+srv://admin:stratos2025@cluster0.cglpxau.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

print("📡 Yeni kimlikle bağlanılıyor...")

try:
    client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())
    client.admin.command('ping')
    print("\n✅ BAŞARILI! Kapı açıldı. Sorun çözüldü.")
    print("Bu kullanıcı adı ve şifreyi diğer kodlara da yazabilirsin.")

except Exception as e:
    print("\n❌ HATA! Hala giriş yapılamıyor.")
    print("Hata Detayı:", e)