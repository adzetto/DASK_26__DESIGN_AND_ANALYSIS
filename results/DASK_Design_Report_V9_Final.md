# DASK 2025 Tasarım Raporu - V9 Final

## 1. Model Özeti

| Parametre | Değer |
|-----------|-------|
| Model | V9 |
| Eleman Sayısı | 4248 |
| Toplam Ağırlık | 1.386 kg |
| Malzeme | Balsa Ahşap |
| Kesit | 6mm × 6mm |
| Ölçek | 1:50 (λ = 50) |

## 2. Yapısal Özellikler

### 2.1 Geometri
- İkiz Kule Yapısı (Twin Towers)
- Model Yüksekliği: 153 cm (Gerçek: 76.5 m)
- Kat Sayısı: 26 (zemin dahil)
- Kat Yüksekliği: 6 cm (model) = 3 m (gerçek)
- Köprü Bağlantısı: y = 7.4 - 8.6 cm aralığı

### 2.2 Malzeme Özellikleri (Balsa)
| Parametre | Değer |
|-----------|-------|
| Elastisite Modülü E | 170 kN/cm² |
| Kayma Modülü G | 65.38 kN/cm² |
| Yoğunluk ρ | 160 kg/m³ |
| Kesit Alanı A | 0.36 cm² |

## 3. Deprem Analizi

### 3.1 Modal Analiz
| Mod | Periyot (s) | Açıklama |
|-----|-------------|----------|
| 1 | 0.0479 | X yönü translasyon |
| 2 | 0.0478 | Y yönü translasyon |
| 3 | 0.0478 | Burulma |

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

### 3.3 Spektral İvme
T1 = 0.0479s < TA = 0.102s (artan bölge)

```
Sae(T1) = (0.4 + 0.6 × T1/TA) × SDS
        = (0.4 + 0.6 × 0.0479/0.102) × 1.008
        = 0.686g
```

## 4. Düzensizlik Kontrolleri

### 4.1 A1a Burulma Düzensizliği

#### TBDY 2018 Tanımı (Madde 3.6.2.1)
"Herhangi bir katta, döşeme düzlemindeki deprem yüklerinin etkisi altında hesaplanan en büyük kat deplasmanının, katta ortalama kat deplasmanına oranı"

#### Hesap Yöntemi - Kenar Bazlı
İkiz kule yapısında köprü bağlantı düğümleri (y=7.4, y=8.6) yapının **kenarı değil**, iki kule arasındaki **bağlantı elemanıdır**. Bu nedenle burulma hesabı yapının kenarlarında (y=0 ve y=16) yapılmıştır.

| Kat | δmax (mm) | δort (mm) | ηbi |
|-----|-----------|-----------|-----|
| 1 | 0.0023 | 0.0021 | 1.112 |
| 5 | 0.0232 | 0.0231 | 1.003 |
| 10 | 0.0639 | 0.0635 | 1.005 |
| 15 | 0.1076 | 0.1072 | 1.002 |
| 20 | 0.1420 | 0.1419 | 1.000 |
| 25 | 0.1670 | 0.1668 | 1.001 |

**Maksimum ηbi = 1.112 < 1.4** ✓

#### Sonuç
- TBDY 2018 sınırı (ηbi < 2.0): **SAĞLANDI** ✓
- 2024 Tebliğ sınırı (ηbi < 1.4): **SAĞLANDI** ✓
- A1a Burulma Düzensizliği: **YOKTUR**

### 4.2 Eksantirisite Kontrolü

| Parametre | Değer | Limit | Durum |
|-----------|-------|-------|-------|
| ex/Lx | 0.005 | < 0.5 | ✓ |
| ey/Ly | 0.034 | < 0.5 | ✓ |

- Kütle Merkezi (CM) ≈ Rijitlik Merkezi (CR)
- Maksimum eksantirisite: 0.54 cm (kat 25, y yönü)

**Eksantirisite Kontrolü: SAĞLANDI** ✓

### 4.3 Göreli Kat Ötelemesi (Drift)
| Kat | δ/h |
|-----|-----|
| 5 | 0.000318 |
| 10 | 0.000589 |
| 15 | 0.000591 |
| 20 | 0.000596 |
| 25 | 0.001168 |

**Maksimum δ/h = 0.00117 << 0.008** ✓

## 5. Ağırlık Kontrolü

| Bileşen | Ağırlık |
|---------|---------|
| Model Toplam | 1.386 kg |
| Yarışma Limiti | 1.400 kg |
| Kalan Bütçe | 0.014 kg |

**1.386 kg < 1.40 kg** ✓

## 6. Final Değerlendirme

### 6.1 Kontrol Özeti
| Kriter | Sonuç | Limit | Durum |
|--------|-------|-------|-------|
| Ağırlık | 1.386 kg | ≤ 1.4 kg | ✓ UYGUN |
| T1 (Periyot) | 0.0479 s | - | ✓ |
| A1a ηbi (2024 Tebliğ) | 1.112 | < 1.4 | ✓ UYGUN |
| Eksantirisite ex/Lx | 0.005 | < 0.5 | ✓ UYGUN |
| Eksantirisite ey/Ly | 0.034 | < 0.5 | ✓ UYGUN |
| Drift δ/h | 0.00117 | ≤ 0.008 | ✓ UYGUN |

### 6.2 Teknik Notlar
1. Burulma hesabı kenar bazlı yapılmıştır (TBDY 2018 yorumu)
2. Köprü bağlantı düğümleri (y=7.4, y=8.6) yapının kenarı olarak kabul edilmemiştir
3. Her iki kule ayrı ayrı değerlendirilmiştir

### 6.3 Sonuç
**V9 modeli tüm DASK 2025 yarışma gerekliliklerini ve 2024 Tebliğ sınırlarını karşılamaktadır.**

---

## Dosyalar
- Model Düğümleri: `data/twin_position_matrix_v9.csv`
- Model Elemanları: `data/twin_connectivity_matrix_v9.csv`
- Analiz Scripti: `scripts/structural_design_check.py`
- Kenar Bazlı Hesap: `scripts/edge_based_torsion.py`
- Eksantirisite Hesabı: `scripts/eccentricity_check.py`

---

**Tarih:** Şubat 2026  
**Analiz Yazılımı:** OpenSeesPy 3.7.0 + Python 3.10  
**Model Versiyonu:** V9 Final
