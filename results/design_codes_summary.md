# TASARIM YÖNETMELİKLERİ ANALİZ RAPORU
## Design Codes Analysis Report for DASK 2025 Competition

---

## 1. TBDY 2018 (Türkiye Bina Deprem Yönetmeliği)
**Sayfa Sayısı:** 416

### 1.1 Deprem Yer Hareketi Düzeyleri
| Düzey | Aşılma Olasılığı | Tekrarlanma Periyodu |
|-------|------------------|---------------------|
| DD-1 | 50 yılda %2 | 2475 yıl |
| DD-2 | 50 yılda %10 | 475 yıl |
| DD-3 | 50 yılda %50 | 72 yıl |
| DD-4 | 50 yılda %68 | 43 yıl |

### 1.2 Tasarım Spektrumu (Madde 2.3.4)
```
T ≤ TA:       Sae(T) = (0.4 + 0.6 T/TA) × SDS
TA < T ≤ TB:  Sae(T) = SDS                      (Plato bölgesi)
TB < T ≤ TL:  Sae(T) = SD1 / T
T > TL:       Sae(T) = SD1 × TL / T²

Köşe periyotları:
  TA = 0.2 × SD1 / SDS
  TB = SD1 / SDS
  TL = 6.0 s
```

### 1.3 Azaltılmış Tasarım İvme Spektrumu (Madde 4.4.1)
```
T < TB:  Ra(T) = D + (R/I - D) × T/TB
T ≥ TB:  Ra(T) = R / I

SaR(T) = Sae(T) / Ra(T)
```

### 1.4 Taşıyıcı Sistem Katsayıları (Tablo 4.1)
| Sistem Tipi | R | D |
|-------------|---|---|
| Süneklik Düzeyi Yüksek Çerçeve | 8 | 3 |
| Süneklik Düzeyi Yüksek Perdeli | 7 | 2.5 |
| Süneklik Düzeyi Sınırlı Çerçeve | 4 | 2.5 |
| Merkezi Çaprazlı Çelik | 5 | 2 |
| Ahşap Çerçeve | 3 | 2 |

### 1.5 Düzensizlik Kontrolleri (Tablo 3.6)

**Plan Düzensizlikleri (A Tipi):**
| Kod | Düzensizlik | Koşul |
|-----|-------------|-------|
| A1a | Burulma | ηbi = δmax/δavg > 1.2 |
| A1b | Döşeme Süreksizliği | Boşluk > 1/3 alan |
| A2 | Planda Çıkıntı | L/B > 0.2 |
| A3 | Perde Süreksizliği | Üstte yok, altta var |

**Düşey Düzensizlikler (B Tipi):**
| Kod | Düzensizlik | Koşul |
|-----|-------------|-------|
| B1 | Dayanım | Qi/Qi+1 < 0.8 |
| B2 | Rijitlik (Yumuşak Kat) | Ki/Ki+1 < 0.8 veya Ki/Kavg3 < 0.6 |
| B3 | Kütle | mi/mi+1 > 1.5 |

### 1.6 Göreli Kat Ötelemesi Sınırları (Madde 4.9.1.3)
```
δi/hi ≤ κ

κ = 0.008  → Genel binalar (dolgu duvarlı)
κ = 0.016  → Esnek bağlantılı dolgu duvarlar
κ = 0.021  → Çelik moment çerçeveler
```

### 1.7 Eşdeğer Deprem Yükü Yöntemi (Madde 4.7)
```
Toplam Deprem Kuvveti:
  Vt = SaR(T1) × W × I / g

Kat Kuvvetleri:
  Fi = (Wi × Hi) / Σ(Wj × Hj) × Vt

Hakim Periyot (yaklaşık):
  T1 = Ct × H^0.75
  Ct = 0.085 (çelik çerçeve)
  Ct = 0.075 (betonarme çerçeve)
  Ct = 0.050 (diğer sistemler)
```

---

## 2. 2024 TBDY Uygulama Tebliği Taslağı (27.05.2024)
**Sayfa Sayısı:** 3

### 2.1 Önemli Değişiklikler ve Zorunluluklar

**BYS ≤ 6 Binalar için Zorunlu Perde Kullanımı:**
```
Perde koşulu: Awi ≥ Ndm / (0.25 × fck)

Perde kesit oranı (Denklem 1):
  Σ(Awi)j / Apj ≥ min(0.002N, 0.02) × SDS

Kolon + Perde kesit oranı (Denklem 2):
  [Σ(Aci)j + Σ(Awi)j] / Apj ≥ max[0.009, min(0.003N, 0.03)] × SDS
```

**BKS = 3 (Yüksek Öneme Sahip) Binalar için:**
- Kolon uzun/kısa kenar oranı ≤ 1.5
- Kolon kesit koşulu: Aci ≥ Ndm / (0.35 × fck)
- Burulma düzensizliği: ηbj ≤ 1.4

**Göreli Kat Ötelemesi Limitleri (Güncellenmiş):**
| Yapı Tipi | Limit |
|-----------|-------|
| Dolgu duvarlı betonarme | 0.010 |
| Esnek bağlantılı dolgu | 0.015 |
| Çelik moment çerçeve | 0.0175 |

---

## 3. TS 498:2021 (Yapı Yükleri Standardı)
**Sayfa Sayısı:** 28

### 3.1 Düşey Hareketli Yükler (Çizelge 6)

| Kullanım | Hesap Değeri (kN/m²) |
|----------|---------------------|
| Çatı arası odalar | 1.5 |
| Konut, büro, teras | 2.0 |
| Sınıflar, yatakhaneler, hastane odaları | 3.5 |
| Camiler, tiyatrolar, spor salonları | 5.0 |
| Mağazalar, lokantalar | 5.0 |
| Kütüphaneler, arşivler | 5.0 |
| Tribünler (sabit olmayan oturma) | 7.5 |
| Garajlar (≤2.5 ton araç) | 5.0 |
| Konut merdivenleri | 3.5 |
| Umuma açık bina merdivenleri | 5.0 |

### 3.2 Rüzgar Yükü (Çizelge 4)

| Yükseklik (m) | Rüzgar Hızı (m/s) | Basınç q (kN/m²) |
|---------------|-------------------|------------------|
| 0 - 8 | 28 | 0.5 |
| 9 - 20 | 36 | 0.8 |
| 21 - 100 | 42 | 1.1 |
| > 100 | 46 | 1.3 |

**Rüzgar Yükü Formülü:**
```
W = Cf × q × A

Cf katsayıları:
  - Kapalı yapı (düz yüzey): 1.2
  - Kule tipi yapı: 1.6
  - Eğimli yüzey: Cf × sin(α)
```

### 3.3 Kar Yükü (Çizelge 3)
Bölgelere göre Sk değerleri (kN/m²):

| Rakım (m) | Bölge 1-3 | Bölge 4-6 | Bölge 7-9 |
|-----------|-----------|-----------|-----------|
| 0-200 | 0.75 | 0.75 | 0.75-0.85 |
| 500 | 0.75 | 0.80 | 0.85-1.00 |
| 1000 | 0.80-1.10 | 1.20-1.35 | 1.40-1.60 |
| >1500 | +15% artış | +15% artış | +15% artış |

### 3.4 Hareketli Yük Azaltması (Madde 16)
**≥3 kattan fazla yük taşıyan elemanlar için:**

| Kat Sayısı | Konut (β) | Atölye (β) |
|------------|----------|-----------|
| 1-3 | 1.00 | 1.00 |
| 4 | 0.95 | 0.98 |
| 5 | 0.88 | 0.94 |
| 6 | 0.80 | 0.90 |
| 7 | 0.71 | 0.86 |
| 8 | 0.65 | 0.83 |
| 9+ | 0.60 | 0.80 |

---

## 4. TS ISO 9194 (Malzeme Yoğunlukları)
**Sayfa Sayısı:** 16

### 4.1 Yapı Malzemesi Yoğunlukları

| Malzeme | Yoğunluk (kg/m³) |
|---------|-----------------|
| Normal beton | 2400 |
| Betonarme | 2500 |
| Çelik | 7850 |
| Ahşap (havada kuru) | 400-600 |
| Balsa | 120-160 |
| Tuğla duvar | 1600-1800 |
| Cam | 2500-2600 |

---

## 5. DASK 2025 Model için Uygulama

### 5.1 Ölçek Modeli Benzeşim Kuralları (1:50)
```
Geometrik ölçek:      λ = 50
Kütle ölçeği:         λ³ = 125000
Periyot ölçeği:       √λ = 7.07
İvme ölçeği:          1/√λ = 0.1414

Model periyodu → Prototip periyodu:
  T_prototip = T_model × √50 = T_model × 7.07
```

### 5.2 Model V9 Sonuçları

| Parametre | Değer |
|-----------|-------|
| T1 (öz ağırlık) | 0.048 s |
| T1 (test yükü) | 0.198 s |
| T1_prototip (öz ağırlık) | 0.34 s |
| T1_prototip (test yükü) | 1.40 s |
| Toplam kütle (yapı) | 1.39 kg |
| Maksimum kütle (yarışma) | 1.40 kg |

### 5.3 Spektral Bölge Analizi

```
AFAD DD-2 Parametreleri (V9 Konumu):
  SS = 0.877,  S1 = 0.243
  FS = 1.149,  F1 = 2.114
  
  SDS = SS × FS = 1.008 g
  SD1 = S1 × F1 = 0.514 g
  
  TA = 0.2 × SD1/SDS = 0.102 s
  TB = SD1/SDS = 0.510 s

Model V9 Spektral Konumu:
  T1 = 0.048 s < TA = 0.102 s → YÜKSELEN BÖLGE ✓
```

### 5.4 Düzensizlik Kontrolleri

| Kontrol | Sonuç |
|---------|-------|
| A1a Burulma (ηbi) | 1.455 (>1.2) - Düzensiz |
| A2 Planda Çıkıntı | Simetrik - OK |
| B2 Yumuşak Kat | Bazı katlarda mevcut |
| B3 Kütle | Düzgün dağılım - OK |
| Eksantrisite | 0.00% - Tam simetrik |
| Göreli Öteleme | 0.00017 << 0.008 - OK |

---

## 6. Sonuç ve Öneriler

### TS-498 Yük Uygulaması:
1. **Yarışma test yükü olarak**: 5.0 kN/m² (genel amaçlı döşeme yükü)
2. **Model için**: 1:50 ölçekte yük = 5.0 × 50 = 250 N/m² = 0.025 kN/m²

### TBDY 2018 Uyumu:
1. Burulma düzensizliği (ηbi = 1.455) mevcut ancak 2.0 limitinin altında
2. Göreli kat ötelemesi limitleri sağlanıyor
3. Simetrik tasarım sayesinde eksantrisite yok

### 2024 Tebliğ Taslağı Değerlendirmesi:
- Yeni göreli öteleme limitleri daha katı (0.01 → 0.0175)
- Perde zorunluluğu BYS ≤ 6 binalar için geçerli
- Model karşılıyor (δ/h = 0.00017 << 0.01)

---
**Rapor Tarihi:** Şubat 2026
**Hazırlayan:** TBDY 2018 Otomatik Analiz Sistemi
