# Robot Vacuum Simulator

Bu proje, robot süpürgelerin karar verme mekanizmalarını öğrenmek için geliştirilmiş bir simülasyon programıdır. Robot tamamen otonom hareket eder ve insan müdahalesi olmadan odaları temizler.

## 🤖 Özellikler

### Robot Davranışları
- **Otonom Navigasyon**: Robot kendi kararlarını vererek hareket eder
- **Sensör Tabanlı Algılama**: Engelleri ve duvarları algılar
- **Duvar Takip Algoritması**: Sistematik temizlik için duvarları takip eder
- **Sıkışma Algılama**: Sıkıştığında kendini kurtarır
- **Akıllı Keşif**: Rastgele ama etkili hareket stratejileri

### Oda Özellikleri
- **Rastgele Oda Üretimi**: Her seferinde farklı oda düzenleri
- **Çeşitli Engeller**: Mobilya, duvarlar ve küçük engeller
- **L-şekilli Odalar**: Karmaşık oda geometrileri
- **Gerçekçi Düzenler**: Gerçek ev ortamlarını simüle eder

### Görsel Özellikler
- **Gerçek Zamanlı İzleme**: Robot hareketlerini canlı görüntüleme
- **Temizlik İzi**: Robottun gittiği yolları gösterir
- **Temizlenen Alanlar**: Hangi bölgelerin temizlendiğini gösterir
- **Durum Bilgileri**: Batarya, verimlilik ve algoritma durumu

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
```bash
pip install pygame
```

### Çalıştırma
```bash
python main.py
```

## 🎮 Kontroller

- **SPACE**: Yeni oda oluştur
- **R**: Robot pozisyonunu sıfırla
- **ESC**: Programdan çık

## 🧠 Robot Karar Verme Algoritmaları

### 1. Keşif Modu (Exploration)
- Rastgele yön değişiklikleri
- Engel algılandığında duvar takip moduna geçiş
- Sistematik alan tarama

### 2. Duvar Takip (Wall Following)
- Sağ/sol duvar takip algoritması
- Engel etrafında dönme
- Köşelerde akıllı navigasyon

### 3. Sıkışma Algılama (Stuck Detection)
- Hareket geçmişi analizi
- Minimum hareket eşik kontrolü
- Otomatik kurtulma manevralar

### 4. Temizlik Optimizasyonu
- Daha önce temizlenen alanları önceliksiz yapma
- Verimli yol planlama
- Enerji tasarrufu algoritmaları

## 📊 Performans Metrikleri

- **Temizlik Verimliliği**: Temizlenen alan yüzdesi
- **Zaman Optimizasyonu**: Temizlik süresi
- **Enerji Tüketimi**: Batarya kullanımı
- **Hareket Verimliliği**: Gereksiz tekrar oranı

## 🔧 Kod Yapısı

```
robot-vacuum-sim/
├── main.py                 # Ana program ve oyun döngüsü
├── robot_vacuum.py         # Robot süpürge sınıfı ve AI algoritmaları
├── room_generator.py       # Rastgele oda üretici
├── simulation.py           # Simülasyon koordinatörü
└── README.md              # Bu dosya
```

### Ana Sınıflar

- **RobotVacuum**: Robot davranışları ve karar verme
- **RoomGenerator**: Rastgele oda düzenleri oluşturma
- **Simulation**: Tüm bileşenleri koordine etme

## 🎯 Eğitim Hedefleri

Bu simülasyon şunları öğretir:

1. **Otonom Sistem Tasarımı**: Robotların nasıl bağımsız karar verdiği
2. **Sensör Entegrasyonu**: Çevre algılama ve yorumlama
3. **Yol Planlama**: Optimal hareket stratejileri
4. **Durum Makineleri**: Robot davranış modelleme
5. **Algoritma Optimizasyonu**: Verimlilik ve performans

## 🔄 Gelecek Geliştirmeler

- [ ] Makine öğrenmesi entegrasyonu
- [ ] Çoklu robot simülasyonu
- [ ] 3D görselleştirme
- [ ] Gerçek robot verilerinden öğrenme
- [ ] Farklı temizlik algoritmaları karşılaştırması

## 📈 Algoritma Analizi

Program şu karar verme stratejilerini kullanır:

1. **Reaktif Davranış**: Anlık sensör verilerine tepki
2. **Planlama**: Kısa vadeli hedef belirleme
3. **Öğrenme**: Hareket geçmişinden faydalanma
4. **Adaptasyon**: Farklı oda tiplerına uyum

Bu simülasyon, modern robot süpürgelerin gerçek dünyada nasıl çalıştığının basitleştirilmiş ama eğitici bir modelidir.