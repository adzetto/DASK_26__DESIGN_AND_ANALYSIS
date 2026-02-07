# DASK 2025 Tasarım Raporu - V10 Final

## 1. Model Özeti

| Parametre | Değer |
|-----------|-------|
| Model | V10 |
| Eleman Sayısı | 4256 |
| Toplam Ağırlık | 1.394 kg |
| Malzeme | Balsa Ahşap |
| Kesit | 6mm × 6mm |
| Ölçek | 1:50 (λ = 50) |

## 2. Yapısal Özellikler

### 2.1 Geometri
- İkiz Kule Yapısı
- Yükseklik: 153 cm (model) = 76.5 m (gerçek)
- Kat Sayısı: 26 (zemin dahil)
- Kat Yüksekliği: 6 cm (model) = 3 m (gerçek)

### 2.2 Malzeme Özellikleri (Balsa)
- Elastisite Modülü E = 170 kN/cm²
- Kayma Modülü G = 65.38 kN/cm²
- Yoğunluk ρ = 160 kg/m³

## 3. Deprem Analizi Sonuçları

### 3.1 Modal Analiz
| Mod | Periyot (s) |
|-----|-------------|
| 1 | 0.0479 |
| 2 | 0.0478 |
| 3 | 0.0478 |

### 3.2 AFAD DD-2 Spektrum Parametreleri
| Parametre | Değer |
|-----------|-------|
| SS | 0.877g |
| S1 | 0.243g |
| FS | 1.149 |
| F1 | 2.114 |
| SDS | 1.008g |
| SD1 | 0.514g |
| TA | 0.102s |
| TB | 0.510s |

### 3.3 Sae(T1) Hesabı
T1 = 0.0479s < TA = 0.102s (artan bölge)

Sae(T1) = (0.4 + 0.6 × T1/TA) × SDS
        = (0.4 + 0.6 × 0.0479/0.102) × 1.008
        = 0.686g

## 4. Düzensizlik Kontrolleri

### 4.1 A1a Burulma Düzensizliği
**Tanım:** ηbi = δmax / δort

| Kat | δmax (mm) | δort (mm) | ηbi |
|-----|-----------|-----------|-----|
| 1 | 0.0047 | 0.0032 | 1.453 |
| 6 | 0.0479 | 0.0476 | 1.007 |
| 11 | 0.1151 | 0.1137 | 1.012 |
| 16 | 0.1881 | 0.1858 | 1.012 |
| 21 | 0.2375 | 0.2366 | 1.003 |

**Maksimum ηbi = 1.453**

- TBDY 2018 sınırı: ηbi < 2.0 ✓ **UYGUN**
- 2024 Tebliğ Taslağı: ηbi < 1.4 (Marjinal aşım: +3.8%)

**Değerlendirme:** 2024 Tebliğ Taslağı henüz yürürlükte değildir. Mevcut TBDY 2018 mevzuatına göre yapı uygundur.

### 4.2 B2 Yumuşak Kat
V10 modelinde köşe çaprazları eklenerek 1. kat rijitliği artırılmıştır.

### 4.3 Göreli Kat Ötelemesi (Drift)
| Kat | δ/h |
|-----|-----|
| 5 | 0.000318 |
| 10 | 0.000589 |
| 15 | 0.000591 |
| 20 | 0.000596 |
| 25 | 0.001168 |

**Maksimum δ/h = 0.00117 << 0.008** ✓ **UYGUN**

## 5. V10 İyileştirmeleri

### 5.1 V9'dan Farklar
V10 modeli, V9'a 8 adet YZ düzlem köşe çaprazı eklenerek oluşturulmuştur:

| Konum | Eleman |
|-------|--------|
| Tower 1, x=0, y=0 | 2 çapraz |
| Tower 1, x=0, y=16 | 2 çapraz |
| Tower 1, x=30, y=0 | 2 çapraz |
| Tower 1, x=30, y=16 | 2 çapraz |

### 5.2 Alternatif Tasarım Denemeleri
| Model | Değişiklik | ηbi | Sonuç |
|-------|------------|-----|-------|
| V10 | YZ köşe çaprazları | 1.453 | En iyi |
| V10b | +XZ köşe çaprazları | 1.469 | Kötüleşti |
| V10c | +XZ merkez çaprazları | 1.726 | Çok kötü |
| V10e | +YZ merkez çaprazları | 1.474 | Kötüleşti |

Ek çaprazlar burulmayı iyileştirmedi, aksine kötüleştirdi. V10 optimal tasarımdır.

## 6. Ağırlık Kontrolü
| Bileşen | Ağırlık |
|---------|---------|
| V10 Model | 1.394 kg |
| Limit | 1.400 kg |
| Kalan Bütçe | 0.006 kg |

**1.394 kg < 1.40 kg** ✓ **UYGUN**

## 7. Sonuç

V10 modeli DASK 2025 yarışması gerekliliklerini karşılamaktadır:

| Kriter | Sonuç | Durum |
|--------|-------|-------|
| Ağırlık ≤ 1.4 kg | 1.394 kg | ✓ |
| Drift δ/h ≤ 0.008 | 0.00117 | ✓ |
| A1a ηbi (TBDY 2018 < 2.0) | 1.453 | ✓ |
| A1a ηbi (2024 Taslak < 1.4) | 1.453 | ≈ |

**Model durumu:** UYGUN (TBDY 2018)

2024 Tebliğ Taslağı sınırı marjinal olarak aşılmaktadır (%3.8), ancak bu taslak henüz yürürlükte olmadığından bağlayıcı değildir.

---

**Tarih:** 2025-01-XX  
**Analiz Yazılımı:** OpenSeesPy + Python  
**Versiyon:** V10 Final
