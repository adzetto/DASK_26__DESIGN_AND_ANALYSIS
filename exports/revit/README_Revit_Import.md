# DASK V9 Twin Towers - Revit Import Kılavuzu

## 1. Genel Bakış

Bu klasör, DASK 2025 V9 ikiz kule yapısal modelini Autodesk Revit'e aktarmak için gerekli dosyaları içerir.

### Model Özellikleri

| Parametre | Model Ölçeği (1:50) | Gerçek Ölçek (1:1) |
|-----------|---------------------|---------------------|
| Toplam Yükseklik | 153 cm | 76.5 m |
| Kat Sayısı | 26 | 26 |
| Düğüm Sayısı | 1,680 | 1,680 |
| Eleman Sayısı | 4,248 | 4,248 |
| Kesit Boyutu | 6mm × 6mm | 300mm × 300mm |
| Malzeme | Balsa Ahşap | Çelik/Beton eşdeğeri |

### Dosya Listesi

```
exports/revit/
├── dask_v9_real_scale.json          # Dynamo JSON - Gerçek ölçek (76.5m)
├── dask_v9_model_scale.json         # Dynamo JSON - Model ölçek (153cm)
├── dask_v9_revit_import_real.py     # RPS Script - Gerçek ölçek
├── dask_v9_revit_import_model.py    # RPS Script - Model ölçek
├── dask_v9_real_scale.ifc           # IFC 4 - Gerçek ölçek
└── README_Revit_Import.md           # Bu dosya
```

---

## 2. Import Yöntemleri

### Yöntem A: Revit Python Shell (RPS) ile Import

**Gereksinimler:**
- Revit 2020 veya üzeri
- Revit Python Shell (RPS) veya pyRevit eklentisi

**Adımlar:**

1. **Revit'i açın** ve yeni bir Structural Template ile proje başlatın

2. **RPS'i başlatın:**
   - pyRevit kullanıyorsanız: `pyRevit > Python Shell`
   - RPS kullanıyorsanız: `Add-Ins > Revit Python Shell`

3. **Script dosyasını açın:**
   - `exports/revit/dask_v9_revit_import_real.py` (gerçek ölçek için)
   - veya `dask_v9_revit_import_model.py` (model ölçek için)

4. **Scripti çalıştırın:**
   - Dosyayı RPS editörüne kopyalayın
   - `Execute` veya `Run` butonuna tıklayın

5. **Sonuçları kontrol edin:**
   - Script otomatik olarak Level'lar oluşturacak
   - Kolonlar, kirişler ve çaprazlar eklenecek
   - Konsol penceresinde ilerleme gösterilecek

**Beklenen Çıktı:**
```
[1/4] Creating levels...
  Created level: Floor_00 at 0.00 ft
  Created level: Floor_01 at 14.76 ft
  ...
[2/4] Loading family types...
[3/4] Creating structural elements...
[4/4] Import complete!
SUMMARY:
  Columns created: 1608
  Beams created: 2120
  Braces created: 520
```

---

### Yöntem B: Dynamo ile Import

**Gereksinimler:**
- Revit 2020 veya üzeri
- Dynamo 2.x (Revit ile birlikte gelir)

**Adımlar:**

1. **Revit'te Dynamo'yu açın:**
   - `Manage > Dynamo`

2. **Yeni bir Dynamo Graph oluşturun**

3. **Gerekli node'ları ekleyin:**

   ```
   [File Path]  →  [Python Script]  →  [Watch]
   ```

   - `File Path` node: JSON dosyasının yolunu seçin
   - `Python Script` node: `scripts/dynamo_revit_import.py` içeriğini kopyalayın
   - `Watch` node: Sonuçları görüntülemek için

4. **Alternatif: Hazır Dynamo Grafiği**

   Aşağıdaki node'ları sırasıyla bağlayın:

   ```
   File.ReadText ("dask_v9_real_scale.json")
        ↓
   Python Script (dynamo_revit_import.py)
        ↓
   StructuralFraming.ByCurve
        ↓
   Watch (Results)
   ```

5. **Graph'ı çalıştırın:**
   - `Run` butonuna tıklayın
   - Import ilerlemesini izleyin

---

### Yöntem C: IFC Import

**Gereksinimler:**
- Revit 2020 veya üzeri
- IFC import desteği (varsayılan olarak etkin)

**Adımlar:**

1. **Revit'i açın** ve yeni proje başlatın

2. **IFC dosyasını import edin:**
   - `Insert > Link IFC` veya `Insert > Import IFC`
   - `dask_v9_real_scale.ifc` dosyasını seçin

3. **Import ayarlarını yapın:**
   - Unit: Meters
   - Positioning: Auto - Internal Origin
   - Category: Structural Framing, Structural Columns

4. **Import'u onaylayın**

**Not:** IFC import, geometriyi doğru aktarır ancak yapısal bağlantıları (analytic lines) yeniden tanımlamanız gerekebilir.

---

## 3. Family Types ve Parametreler

### Önerilen Family Types

Import sırasında script aşağıdaki family type'ları aramaya çalışır:

| Eleman Tipi | Aranan Family | Alternatif |
|-------------|---------------|------------|
| Column | HSS6x6x.375 | W10x33, M_W-Wide Flange |
| Beam | W10x26 | HSS6x6, M_Concrete-Rectangular |
| Brace | HSS4x4x.250 | L4x4x1/4, HSS Round |

### Kesit Boyutları

Gerçek ölçekte (1:1):
- Model 6mm → 300mm (6mm × 50)
- HSS300x300 veya W310 eşdeğeri

Model ölçekte (1:50):
- 6mm × 6mm kare kesit
- Custom family gerekebilir

### Custom Family Oluşturma

6mm × 6mm balsa kesiti için custom family:

1. `File > New > Family > Metric Structural Framing`
2. Extrusion ile 6mm × 6mm kare kesit çizin
3. Family parametrelerini ayarlayın
4. `Load into Project`

---

## 4. Koordinat Sistemi

### Model Orijini

```
Model Origin: (0, 0, 0)
  ├── Tower 1: X[0, 30] Y[0, 16] cm
  ├── Tower 2: X[0, 30] Y[24, 40] cm
  └── Bridge:  X[11, 19] Y[16, 24] cm (ara bağlantı)
```

### Revit Koordinat Dönüşümü

```
Revit XYZ = Model XYZ × Scale Factor × (1 ft / 30.48 cm)

Gerçek Ölçek:
  X_revit = X_model × 50 / 30.48 = X_model × 1.6404 (cm → ft)

Model Ölçek:
  X_revit = X_model / 30.48 (cm → ft)
```

---

## 5. Yapısal Analiz Entegrasyonu

### Revit → Robot Structural Analysis

1. Import tamamlandıktan sonra:
   - `Analyze > Structural Analysis`
   - Boundary conditions tanımlayın (zemin kat sabitlenmeli)
   - Modal analysis parametrelerini ayarlayın

2. Beklenen sonuçlar (referans):
   - T1 ≈ 2.4 s (gerçek ölçek, 76.5m yükseklik)
   - Model ölçekte: T_model = T_real / √λ = 2.4 / √50 ≈ 0.34 s

### ETABS/SAP2000 ile Karşılaştırma

Mevcut OpenSees analizi sonuçları:
- T1 = 0.0479 s (model ölçek)
- ηbi = 1.112 (A1a burulma düzensizliği)
- δ/h = 0.00117 (drift)

---

## 6. Sık Karşılaşılan Sorunlar

### Problem: "Family type not found"

**Çözüm:**
- Structural template kullandığınızdan emin olun
- Gerekli family'leri manuel olarak yükleyin:
  `Insert > Load Family > Structural Framing/Columns`

### Problem: "Transaction failed"

**Çözüm:**
- Revit'te aktif bir view olduğundan emin olun
- Edit mode'da olmadığınızdan emin olun
- Undo geçmişini temizleyin

### Problem: "Line is too short"

**Çözüm:**
- Model ölçekte bazı elemanlar Revit'in minimum uzunluk sınırının altında kalabilir
- Gerçek ölçek import kullanın veya scale factor'ü artırın

### Problem: "Levels overlap"

**Çözüm:**
- Mevcut level'ları import öncesi silin veya
- Script'te level oluşturmayı devre dışı bırakın

---

## 7. Akademik Referans

Bu export yöntemi aşağıdaki standartlara uygundur:

1. **IFC 4 (ISO 16739-1:2018)** - Industry Foundation Classes
2. **Revit API 2024** - Autodesk Developer Documentation
3. **TBDY 2018** - Türkiye Bina Deprem Yönetmeliği
4. **AFAD DD-2** - Deprem Tehlike Haritası Spektrumu

### Atıf

```
DASK 2025 Twin Towers Structural Model V9
Exported via Python Revit API Interface
February 2026
```

---

## 8. Destek

Teknik sorular için:
- OpenSees analiz dosyaları: `scripts/` klasörü
- Model verileri: `data/twin_position_matrix_v9.csv`
- Analiz raporları: `results/DASK_Design_Report_V9_Final.md`

---

**Son Güncelleme:** Şubat 2026
**Model Versiyonu:** V9 Final
**Script Versiyonu:** 1.0
