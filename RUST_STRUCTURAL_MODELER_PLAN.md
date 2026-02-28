# DASK Structural Modeler — Rust Implementation Plan

> **Proje Adı:** `dask-modeler`
> **Dil:** Rust (2024 edition)
> **Platform:** WSL2 (Ubuntu) — cross-compile Windows/Linux/WASM
> **Tarih:** 2026-02-19
> **Hedef:** SAP2000 / Tekla Structures benzeri interaktif 3D yapısal modelleme uygulaması

---

## 1. PROJE GENEL BAKIŞ

### 1.1 Amaç

Mevcut DASK 2026 ikiz kule modelinin (442 düğüm, 2138 eleman, 9 eleman tipi) interaktif olarak
görüntülenmesi, düzenlenmesi ve dışa aktarılması için Rust tabanlı bir masaüstü uygulaması geliştirmek.

### 1.2 Temel Yetenekler

| # | Yetenek | Açıklama |
|---|---------|----------|
| 1 | **3D İnteraktif Görüntüleme** | Orbit/pan/zoom kameralı wireframe + extruded section görünümü |
| 2 | **Section Cutting (Kesit Düzlemleri)** | XY, XZ, YZ hyperplane'leri ile modeli dilimleyip 2D kesit görünümü |
| 3 | **Element Çizimi** | 3D sahne üzerinde interaktif olarak line element (kiriş, kolon, çapraz) ekleme |
| 4 | **Element Düzenleme** | Seçme, taşıma, kopyalama, silme, mirror, linear array |
| 5 | **Kesit & Malzeme Atama** | Dikdörtgen, I-profil, dairesel kesit tanımı ve atama |
| 6 | **Section Display** | Sol panelde 2D kesit görünümleri, sağda 3D model |
| 7 | **Connectivity Matrix Export** | CSV/JSON formatında bağlantı ve komşuluk matrisi çıktısı |
| 8 | **Adjacency Matrix Export** | Seyrek (sparse) matris formatında dışa aktarım |
| 9 | **Undo/Redo** | Sınırsız geri alma / yineleme |
| 10 | **Dosya I/O** | Proje kaydetme/yükleme (JSON), CSV import/export |

### 1.3 Mevcut Veri Yapısı (DASK 2026 Modeli)

```
data/
├── position_matrix.csv      # 442 düğüm: node_id, x, y, z, floor, zone
├── connectivity_matrix.csv  # 2138 eleman: element_id, node_i, node_j, element_type, length
├── adjacency_matrix.csv     # 442×442 seyrek matris (0/1)
└── building_data.npz        # NumPy binary
```

**Düğüm Bölgeleri:** podium (234), tower (156), chevron_node (52)

**Eleman Tipleri ve Sayıları:**

| Tip | Sayı | Açıklama |
|-----|------|----------|
| `brace_floor` | 416 | Döşeme çaprazı |
| `column` | 372 | Düşey kolon |
| `beam_x` | 312 | X doğrultusunda kiriş |
| `core_wall` | 300 | Çekirdek duvar elemanı |
| `beam_y` | 260 | Y doğrultusunda kiriş |
| `brace_xz` | 216 | XZ düzleminde çapraz |
| `brace_yz` | 144 | YZ düzleminde çapraz |
| `chevron` | 100 | Ters V çapraz |
| `brace_space` | 18 | Uzay çapraz (köprü) |

**Koordinat Aralıkları:**
- X: 0.0 — 20.0 (cm, model ölçeği)
- Y: 0.0 — 16.0
- Z: 0.0 — 153.0 (25 kat)

---

## 2. TEKNOLOJİ YIĞINI (TECHNOLOGY STACK)

### 2.1 Ana Motor: Bevy ECS (v0.17)

**Seçim Gerekçesi:**
- Entity-Component-System mimarisi her yapısal elemanı bir entity olarak modellemeye birebir uygun
- Dahili **Gizmo** sistemi ile çizgi (line) rendering — yapısal wireframe için ideal
- Dahili **picking** sistemi — element seçimi hazır
- **Viewport Node** (v0.17) — 3D sahneyi UI node içinde render edebilme
- `bevy_egui` entegrasyonu ile paneller + 3D aynı pencerede
- Cross-platform: Windows, Linux, macOS, WASM

### 2.2 GUI: egui (v0.33) + bevy_egui (v0.38)

**Seçim Gerekçesi:**
- Immediate-mode GUI — property editor'ler seçim durumunu anında yansıtır
- Panel layout: `SidePanel`, `TopBottomPanel`, `CentralPanel` → sol/sağ/alt paneller
- Dahili widget'lar: slider, combo box, tree view, color picker, text input
- 3D sahneyi texture olarak render edip egui'de gösterebilme (2D kesit paneli için)

### 2.3 Kamera: bevy_panorbit_camera (v0.25)

- Orbit (sağ tık + sürükle)
- Pan (orta tık + sürükle)
- Zoom (scroll)
- Ortografik / perspektif geçişi

### 2.4 Matematik: nalgebra (v0.33) + glam (Bevy dahili)

| Kütüphane | Kullanım Alanı |
|-----------|---------------|
| `glam` | 3D grafik transformasyonları (Bevy ile gelir) |
| `nalgebra` | Mühendislik matematiği, dinamik matrisler, düzlem denklemleri |
| `nalgebra-sparse` | CSR/CSC seyrek matrisler (adjacency matrix) |

### 2.5 Dosya I/O: serde + csv

| Crate | Versiyon | Kullanım |
|-------|----------|----------|
| `serde` | 1.0 | Serialize/Deserialize tüm veri yapıları |
| `serde_json` | 1.0 | Proje dosyası (.json) kaydet/yükle |
| `csv` | 1.4 | CSV import/export (connectivity, position matrix) |

### 2.6 Tam Bağımlılık Listesi

```toml
[package]
name = "dask-modeler"
version = "0.1.0"
edition = "2024"

[dependencies]
# Motor & Rendering
bevy = { version = "0.17", features = ["default"] }
bevy_egui = "0.38"
bevy_panorbit_camera = "0.25"

# Matematik
nalgebra = "0.33"
nalgebra-sparse = "0.10"

# Serialization & I/O
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
csv = "1.4"

# Yardımcı
log = "0.4"
env_logger = "0.11"

[profile.dev]
opt-level = 1           # Bevy debug build hızlandırma

[profile.dev.package."*"]
opt-level = 3           # Bağımlılıklar tam optimizasyon
```

---

## 3. MİMARİ TASARIM (ARCHITECTURE)

### 3.1 Modül Haritası

```
dask-modeler/
├── Cargo.toml
├── src/
│   ├── main.rs                    # Bevy App builder, plugin registration
│   ├── lib.rs                     # Public API, re-exports
│   │
│   ├── model/                     # Veri modeli (ECS-bağımsız çekirdek)
│   │   ├── mod.rs
│   │   ├── node.rs                # Node struct, koordinatlar, kısıtlar
│   │   ├── element.rs             # Element struct, tip enum, connectivity
│   │   ├── section.rs             # Kesit tanımları (dikdörtgen, I, daire)
│   │   ├── material.rs            # Malzeme tanımları (E, G, ν, ρ)
│   │   ├── project.rs             # Proje container (tüm model verisi)
│   │   ├── connectivity.rs        # Connectivity matrix hesaplama
│   │   ├── adjacency.rs           # Adjacency matrix hesaplama (sparse)
│   │   └── validation.rs          # Model doğrulama (orphan node, zero-length, vb.)
│   │
│   ├── ecs/                       # Bevy ECS bileşenleri ve sistemleri
│   │   ├── mod.rs
│   │   ├── components.rs          # StructuralNode, StructuralElement, Selected, vb.
│   │   ├── resources.rs           # AppState, SectionPlanes, ToolMode, UndoStack
│   │   ├── systems/
│   │   │   ├── mod.rs
│   │   │   ├── render.rs          # Gizmo çizim, renk atama, label render
│   │   │   ├── picking.rs         # Ray-cast seçim, hover highlight
│   │   │   ├── camera.rs          # Kamera kontrol sistemi
│   │   │   ├── grid.rs            # Grid çizim sistemi
│   │   │   ├── section_cut.rs     # Kesit düzlemi render + 2D projeksiyon
│   │   │   ├── drawing.rs         # Element çizim modu (node-to-node)
│   │   │   ├── transform.rs       # Move, copy, mirror, array işlemleri
│   │   │   └── input.rs           # Klavye/mouse input handling
│   │   └── events.rs              # Custom events (ElementAdded, NodeMoved, vb.)
│   │
│   ├── ui/                        # egui panelleri
│   │   ├── mod.rs
│   │   ├── toolbar.rs             # Üst toolbar (dosya, araç seçimi, görünüm)
│   │   ├── properties_panel.rs    # Sağ panel (seçili eleman özellikleri)
│   │   ├── model_tree.rs          # Sol panel (model ağacı: malzeme, kesit, katlar)
│   │   ├── section_view.rs        # Sol alt panel (2D kesit görünümü)
│   │   ├── status_bar.rs          # Alt durum çubuğu (koordinat, seçim, istatistik)
│   │   ├── section_plane_controls.rs  # Kesit düzlemi slider'ları
│   │   ├── element_table.rs       # Eleman tablosu (tablo görünümü)
│   │   ├── dialogs/
│   │   │   ├── mod.rs
│   │   │   ├── new_section.rs     # Yeni kesit tanımlama dialogu
│   │   │   ├── new_material.rs    # Yeni malzeme tanımlama dialogu
│   │   │   ├── export.rs          # Dışa aktarım seçenekleri
│   │   │   ├── import.rs          # İçe aktarım (CSV)
│   │   │   └── coordinate_input.rs # Koordinat girişi dialogu
│   │   └── theme.rs               # egui tema ve renk ayarları
│   │
│   ├── io/                        # Dosya işlemleri
│   │   ├── mod.rs
│   │   ├── csv_io.rs              # CSV okuma/yazma
│   │   ├── json_project.rs        # JSON proje dosyası
│   │   ├── matrix_export.rs       # Connectivity & adjacency matrix export
│   │   └── opensees_export.rs     # OpenSees TCL dosya üretimi
│   │
│   ├── commands/                  # Undo/Redo command pattern
│   │   ├── mod.rs
│   │   ├── command.rs             # Command trait tanımı
│   │   ├── undo_stack.rs          # UndoStack veri yapısı
│   │   ├── add_node.rs            # Düğüm ekleme komutu
│   │   ├── add_element.rs         # Eleman ekleme komutu
│   │   ├── delete_elements.rs     # Eleman silme komutu
│   │   ├── move_nodes.rs          # Düğüm taşıma komutu
│   │   ├── copy_elements.rs       # Eleman kopyalama komutu
│   │   ├── mirror_elements.rs     # Eleman aynalama komutu
│   │   ├── assign_section.rs      # Kesit atama komutu
│   │   └── assign_material.rs     # Malzeme atama komutu
│   │
│   └── shaders/                   # WGSL shader dosyaları
│       ├── section_cut.wgsl       # Kesit düzlemi fragment discard shader
│       ├── element_highlight.wgsl # Seçili eleman highlight shader
│       └── grid.wgsl              # Grid çizim shader
│
├── assets/                        # Statik kaynaklar
│   ├── icons/                     # Toolbar ikonları
│   ├── shaders/                   # Bevy asset olarak shader'lar
│   └── fonts/                     # Türkçe karakter destekli fontlar
│
└── tests/
    ├── model_tests.rs             # Veri modeli unit testleri
    ├── connectivity_tests.rs      # Connectivity matrix testleri
    ├── io_tests.rs                # Import/export testleri
    └── command_tests.rs           # Undo/redo testleri
```

### 3.2 ECS Veri Modeli (Bevy Components)

```rust
// ============================================================
// src/ecs/components.rs
// ============================================================

use bevy::prelude::*;
use serde::{Serialize, Deserialize};

// ---- Düğüm (Node) ----

#[derive(Component, Clone, Debug, Serialize, Deserialize)]
pub struct StructuralNode {
    pub id: u32,
    pub position: [f64; 3],     // [x, y, z] gerçek koordinatlar
    pub floor: u32,
    pub zone: NodeZone,
    pub restraints: [bool; 6],  // [Ux, Uy, Uz, Rx, Ry, Rz]
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum NodeZone {
    Podium,
    Tower,
    ChevronNode,
    Bridge,
    Custom(String),
}

// ---- Eleman (Element) ----

#[derive(Component, Clone, Debug, Serialize, Deserialize)]
pub struct StructuralElement {
    pub id: u32,
    pub node_i: u32,            // Başlangıç düğümü
    pub node_j: u32,            // Bitiş düğümü
    pub element_type: ElementType,
    pub section_id: Option<u32>,
    pub material_id: Option<u32>,
    pub releases_i: [bool; 6],  // I-ucu serbestlikleri
    pub releases_j: [bool; 6],  // J-ucu serbestlikleri
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ElementType {
    BeamX,
    BeamY,
    Column,
    BraceXZ,
    BraceYZ,
    BraceFloor,
    CoreWall,
    Chevron,
    BraceSpace,
    Custom(String),
}

impl ElementType {
    /// CSV'deki string'den dönüşüm
    pub fn from_str(s: &str) -> Self {
        match s {
            "beam_x" => Self::BeamX,
            "beam_y" => Self::BeamY,
            "column" => Self::Column,
            "brace_xz" => Self::BraceXZ,
            "brace_yz" => Self::BraceYZ,
            "brace_floor" => Self::BraceFloor,
            "core_wall" => Self::CoreWall,
            "chevron" => Self::Chevron,
            "brace_space" => Self::BraceSpace,
            other => Self::Custom(other.to_string()),
        }
    }

    /// Varsayılan renk (RGBA)
    pub fn default_color(&self) -> Color {
        match self {
            Self::BeamX      => Color::srgb(0.2, 0.6, 1.0),   // Mavi
            Self::BeamY      => Color::srgb(0.2, 0.8, 0.6),   // Turkuaz
            Self::Column     => Color::srgb(1.0, 0.3, 0.3),   // Kırmızı
            Self::BraceXZ    => Color::srgb(1.0, 0.8, 0.2),   // Sarı
            Self::BraceYZ    => Color::srgb(1.0, 0.5, 0.0),   // Turuncu
            Self::BraceFloor => Color::srgb(0.6, 0.4, 0.8),   // Mor
            Self::CoreWall   => Color::srgb(0.5, 0.5, 0.5),   // Gri
            Self::Chevron    => Color::srgb(0.0, 0.8, 0.0),   // Yeşil
            Self::BraceSpace => Color::srgb(1.0, 0.0, 1.0),   // Magenta
            Self::Custom(_)  => Color::WHITE,
        }
    }
}

// ---- Tag Components ----

#[derive(Component)]
pub struct Selected;

#[derive(Component)]
pub struct Hovered;

#[derive(Component)]
pub struct Visible;

#[derive(Component)]
pub struct NodeMarker;    // Düğüm entity'lerini ayırt etmek için

#[derive(Component)]
pub struct ElementMarker; // Eleman entity'lerini ayırt etmek için
```

### 3.3 Uygulama Durumu (Resources)

```rust
// ============================================================
// src/ecs/resources.rs
// ============================================================

use bevy::prelude::*;

/// Aktif araç modu
#[derive(Resource, Default, PartialEq, Eq, Clone, Copy)]
pub enum ToolMode {
    #[default]
    Select,           // Seçim modu (varsayılan)
    DrawBeam,         // Kiriş çizim modu
    DrawColumn,       // Kolon çizim modu
    DrawBrace,        // Çapraz çizim modu
    MoveNode,         // Düğüm taşıma modu
    Pan,              // Kamera pan modu
}

/// Kesit düzlemi kontrolleri
#[derive(Resource)]
pub struct SectionPlanes {
    pub xy_enabled: bool,     // XY düzlemi aktif mi?
    pub xy_z: f32,            // XY düzleminin Z konumu
    pub xz_enabled: bool,     // XZ düzlemi aktif mi?
    pub xz_y: f32,            // XZ düzleminin Y konumu
    pub yz_enabled: bool,     // YZ düzlemi aktif mi?
    pub yz_x: f32,            // YZ düzleminin X konumu
    pub depth: f32,           // Görünüm derinliği (kesit kalınlığı)
}

impl Default for SectionPlanes {
    fn default() -> Self {
        Self {
            xy_enabled: false, xy_z: 0.0,
            xz_enabled: false, xz_y: 8.0,
            yz_enabled: false, yz_x: 10.0,
            depth: 1.0,
        }
    }
}

/// Görüntü ayarları
#[derive(Resource)]
pub struct DisplaySettings {
    pub show_nodes: bool,
    pub show_labels: bool,
    pub show_grid: bool,
    pub show_axes: bool,
    pub show_extruded: bool,       // Extruded section görünümü
    pub show_local_axes: bool,     // Eleman lokal eksen okları
    pub show_releases: bool,       // Mafsal göstergesi
    pub color_mode: ColorMode,
    pub grid_spacing: f32,
    pub node_size: f32,
    pub line_width: f32,
}

#[derive(Default, PartialEq, Eq, Clone, Copy)]
pub enum ColorMode {
    #[default]
    ByElementType,    // Eleman tipine göre renk
    BySection,        // Kesite göre renk
    ByMaterial,       // Malzemeye göre renk
    ByFloor,          // Kata göre renk
    Uniform,          // Tek renk
}

impl Default for DisplaySettings {
    fn default() -> Self {
        Self {
            show_nodes: true,
            show_labels: false,
            show_grid: true,
            show_axes: true,
            show_extruded: false,
            show_local_axes: false,
            show_releases: false,
            color_mode: ColorMode::ByElementType,
            grid_spacing: 1.0,
            node_size: 0.15,
            line_width: 2.0,
        }
    }
}

/// Snap ayarları
#[derive(Resource)]
pub struct SnapSettings {
    pub snap_to_grid: bool,
    pub snap_to_node: bool,
    pub snap_to_midpoint: bool,
    pub snap_distance: f32,      // Snap yakalama mesafesi (piksel)
    pub grid_snap_size: f32,     // Grid snap adımı
}

impl Default for SnapSettings {
    fn default() -> Self {
        Self {
            snap_to_grid: true,
            snap_to_node: true,
            snap_to_midpoint: false,
            snap_distance: 15.0,
            grid_snap_size: 1.0,
        }
    }
}

/// Çizim modu durumu
#[derive(Resource, Default)]
pub struct DrawingState {
    pub first_node: Option<u32>,     // İlk tıklanan düğüm
    pub preview_end: Option<Vec3>,   // Mouse konumundaki preview uç nokta
    pub continuous: bool,            // Sürekli çizim modu
    pub element_type: ElementType,   // Çizilecek eleman tipi
}

/// Seçim durumu
#[derive(Resource, Default)]
pub struct SelectionState {
    pub selected_nodes: Vec<u32>,
    pub selected_elements: Vec<u32>,
    pub box_select_start: Option<Vec2>,  // Kutu seçim başlangıcı
}

/// Model istatistikleri (status bar için)
#[derive(Resource, Default)]
pub struct ModelStats {
    pub total_nodes: usize,
    pub total_elements: usize,
    pub total_dofs: usize,
    pub selected_count: usize,
    pub cursor_world_pos: Vec3,
}
```

### 3.4 Veri Modeli Çekirdeği (ECS-bağımsız)

```rust
// ============================================================
// src/model/project.rs
// ============================================================

use serde::{Serialize, Deserialize};
use std::collections::HashMap;

/// Tüm proje verisi — serialize edilebilir, ECS'den bağımsız
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Project {
    pub name: String,
    pub version: String,
    pub units: Units,
    pub nodes: HashMap<u32, NodeData>,
    pub elements: HashMap<u32, ElementData>,
    pub sections: HashMap<u32, SectionDef>,
    pub materials: HashMap<u32, MaterialDef>,
    pub next_node_id: u32,
    pub next_element_id: u32,
    pub next_section_id: u32,
    pub next_material_id: u32,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct NodeData {
    pub id: u32,
    pub x: f64,
    pub y: f64,
    pub z: f64,
    pub floor: u32,
    pub zone: String,
    pub restraints: [bool; 6],
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ElementData {
    pub id: u32,
    pub node_i: u32,
    pub node_j: u32,
    pub element_type: String,
    pub section_id: Option<u32>,
    pub material_id: Option<u32>,
    pub releases_i: [bool; 6],
    pub releases_j: [bool; 6],
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub enum SectionShape {
    Rectangular { width: f64, height: f64 },
    IBeam { flange_w: f64, flange_t: f64, web_h: f64, web_t: f64 },
    Circular { diameter: f64 },
    Pipe { outer_d: f64, inner_d: f64 },
    LAngle { leg_a: f64, leg_b: f64, thickness: f64 },
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SectionDef {
    pub id: u32,
    pub name: String,
    pub shape: SectionShape,
    pub area: f64,          // A
    pub ix: f64,            // Ix (strong axis)
    pub iy: f64,            // Iy (weak axis)
    pub j: f64,             // Torsional constant
    pub color: [f32; 3],    // Display color RGB
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct MaterialDef {
    pub id: u32,
    pub name: String,
    pub e: f64,             // Young's modulus
    pub g: f64,             // Shear modulus
    pub nu: f64,            // Poisson's ratio
    pub density: f64,       // Yoğunluk
    pub fy: f64,            // Akma dayanımı
    pub fu: f64,            // Çekme dayanımı
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Units {
    pub length: String,     // "cm", "m", "mm"
    pub force: String,      // "kN", "N", "kgf"
    pub mass: String,       // "kg", "t"
}
```

---

## 4. KESİT DÜZLEM SİSTEMİ (SECTION CUTTING)

### 4.1 Hyperplane Matematiği

Bir düzlem (hyperplane), 3B uzayda bir normal vektör `n` ve bir nokta `p₀` ile tanımlanır:

```
n · (p - p₀) = 0
```

Üç standart kesit düzlemi:

| Düzlem | Normal | Konum Parametresi |
|--------|--------|-------------------|
| XY (kat planı) | n = (0, 0, 1) | z = z₀ |
| XZ (ön görünüş) | n = (0, 1, 0) | y = y₀ |
| YZ (yan görünüş) | n = (1, 0, 0) | x = x₀ |

### 4.2 Fragment Shader ile Görsel Kırpma (3D Viewport)

```wgsl
// assets/shaders/section_cut.wgsl

struct ClipPlane {
    normal: vec3<f32>,
    distance: f32,
    enabled: u32,
    _padding: vec3<f32>,
};

struct ClipUniforms {
    planes: array<ClipPlane, 3>,  // XY, XZ, YZ
};

@group(2) @binding(0)
var<uniform> clip: ClipUniforms;

@fragment
fn fragment(input: VertexOutput) -> @location(0) vec4<f32> {
    let world_pos = input.world_position.xyz;

    // Her aktif düzlem için kontrol
    for (var i = 0u; i < 3u; i = i + 1u) {
        if (clip.planes[i].enabled != 0u) {
            let signed_dist = dot(clip.planes[i].normal, world_pos) - clip.planes[i].distance;
            if (signed_dist > 0.0) {
                discard;
            }
        }
    }

    return input.color;
}
```

### 4.3 Geometrik Kesit Çıkartma (2D Kesit Paneli)

```rust
// src/ecs/systems/section_cut.rs

use nalgebra::{Point3, Vector3};

pub struct ClipPlane {
    pub normal: Vector3<f64>,
    pub point: Point3<f64>,
}

impl ClipPlane {
    /// Noktanın düzleme olan işaretli mesafesi
    pub fn signed_distance(&self, p: &Point3<f64>) -> f64 {
        self.normal.dot(&(p - self.point))
    }

    /// Çizgi segmentinin düzlemle kesişim noktası
    pub fn intersect_segment(
        &self,
        a: &Point3<f64>,
        b: &Point3<f64>,
    ) -> Option<Point3<f64>> {
        let da = self.signed_distance(a);
        let db = self.signed_distance(b);
        // Aynı tarafta ise kesişim yok
        if da * db >= 0.0 {
            return None;
        }
        let t = da / (da - db);
        Some(Point3::from(a.coords.lerp(&b.coords, t)))
    }
}

/// Bir düzlemle kesişen tüm elemanları bulup 2D noktalar döndür
pub fn extract_section_intersections(
    nodes: &[(u32, Point3<f64>)],
    elements: &[(u32, u32, u32, String)],  // (id, node_i, node_j, type)
    plane: &ClipPlane,
    depth: f64,
) -> Vec<SectionIntersection> {
    let node_map: HashMap<u32, &Point3<f64>> = nodes.iter()
        .map(|(id, pos)| (*id, pos))
        .collect();

    elements.iter().filter_map(|(id, ni, nj, etype)| {
        let a = node_map.get(ni)?;
        let b = node_map.get(nj)?;
        let da = plane.signed_distance(a).abs();
        let db = plane.signed_distance(b).abs();

        // Eleman düzlemi kesiyor veya düzleme yeterince yakın
        if let Some(intersection) = plane.intersect_segment(a, b) {
            let point_2d = project_to_plane_coords(&intersection, plane);
            Some(SectionIntersection {
                element_id: *id,
                element_type: etype.clone(),
                point_2d,
                is_crossing: true,
            })
        } else if da < depth || db < depth {
            // Eleman düzleme yakın — derinlik içinde
            let midpoint = Point3::from((a.coords + b.coords) * 0.5);
            let point_2d = project_to_plane_coords(&midpoint, plane);
            Some(SectionIntersection {
                element_id: *id,
                element_type: etype.clone(),
                point_2d,
                is_crossing: false,
            })
        } else {
            None
        }
    }).collect()
}

/// 3D noktayı düzlem koordinat sistemine projekte et → 2D
fn project_to_plane_coords(
    point: &Point3<f64>,
    plane: &ClipPlane,
) -> [f64; 2] {
    let n = &plane.normal;
    // Düzlem normal vektörüne göre U ve V eksenleri oluştur
    let up = if n.z.abs() < 0.9 {
        Vector3::z()
    } else {
        Vector3::x()
    };
    let u = n.cross(&up).normalize();
    let v = n.cross(&u).normalize();

    let diff = point - plane.point;
    [diff.dot(&u), diff.dot(&v)]
}

pub struct SectionIntersection {
    pub element_id: u32,
    pub element_type: String,
    pub point_2d: [f64; 2],
    pub is_crossing: bool,
}
```

### 4.4 Section Display — Sol Panel 2D Görünüm

```
+---------------------------+
| Section View: XZ @ Y=8.0 |
| [dropdown: XY|XZ|YZ]     |
|                           |
|     ·  |  ·  |  ·        |  ← Düğümler nokta olarak
|     |  |  |  |  |        |
|     ·--+--·--+--·        |  ← Elemanlar çizgi olarak
|     |  |  |  |  |        |
|     ·  |  ·  |  ·        |
|     |\ | /|\ | /|        |  ← Çaprazlar
|     | \|/ | \|/ |        |
|     ·--+--·--+--·        |
|                           |
| Z: [====|==========] 50  |  ← Düzlem pozisyon slider
| Depth: [==|======] 2.0   |  ← Derinlik slider
+---------------------------+
```

---

## 5. 3D İNTERAKTİF ÇİZİM SİSTEMİ

### 5.1 Element Çizim Modu

```
Kullanıcı Akışı:
1. Toolbar'dan "Kiriş Çiz" veya "Kolon Çiz" aracını seç
2. ToolMode → DrawBeam / DrawColumn / DrawBrace
3. 3D viewport'ta bir düğüme tıkla → DrawingState.first_node = Some(node_id)
4. Mouse hareket eder → preview çizgi (noktalı) gösterilir
5. İkinci düğüme tıkla → Element oluşturulur, Command stack'e eklenir
6. Continuous modda → ikinci düğüm birinci düğüm olur, çizim devam eder
7. ESC veya sağ tık → çizim modu iptal
```

### 5.2 Snap Sistemi

```rust
// src/ecs/systems/drawing.rs

/// Verilen ekran konumuna en yakın snap hedefini bul
fn find_snap_target(
    cursor_screen: Vec2,
    camera: &Camera,
    transform: &GlobalTransform,
    nodes: &Query<(&StructuralNode, &GlobalTransform)>,
    snap_settings: &SnapSettings,
) -> Option<SnapTarget> {
    let mut best: Option<(f32, SnapTarget)> = None;

    // 1. Düğüm snap (en yüksek öncelik)
    if snap_settings.snap_to_node {
        for (node, node_transform) in nodes.iter() {
            let world_pos = node_transform.translation();
            if let Ok(screen_pos) = camera.world_to_viewport(transform, world_pos) {
                let dist = cursor_screen.distance(screen_pos);
                if dist < snap_settings.snap_distance {
                    if best.is_none() || dist < best.as_ref().unwrap().0 {
                        best = Some((dist, SnapTarget::Node(node.id, world_pos)));
                    }
                }
            }
        }
    }

    // 2. Grid snap
    if snap_settings.snap_to_grid && best.is_none() {
        if let Some(ray) = camera.viewport_to_world(transform, cursor_screen) {
            // Ray-plane intersection ile çalışma düzlemiyle kesişim bul
            let grid_point = snap_to_grid(ray, snap_settings.grid_snap_size);
            best = Some((0.0, SnapTarget::Grid(grid_point)));
        }
    }

    best.map(|(_, target)| target)
}

pub enum SnapTarget {
    Node(u32, Vec3),       // Mevcut düğüm
    Grid(Vec3),            // Grid kesişimi
    Midpoint(Vec3),        // Eleman orta noktası
    Free(Vec3),            // Serbest nokta
}
```

### 5.3 Element Kopyalama ve Dönüştürme

```rust
// Doğrusal (Linear) Kopyalama
pub struct LinearCopyParams {
    pub dx: f64,
    pub dy: f64,
    pub dz: f64,
    pub count: u32,          // Kaç kopya
    pub include_original: bool,
}

// Aynalama (Mirror)
pub struct MirrorParams {
    pub plane: MirrorPlane,
    pub position: f64,        // Düzlem konumu
    pub keep_original: bool,
}

pub enum MirrorPlane {
    XY(f64),  // z = val düzleminde aynala
    XZ(f64),  // y = val düzleminde aynala
    YZ(f64),  // x = val düzleminde aynala
}

// Linear Array (Çok katlı bina oluşturma)
// Örnek: Bir kat planını 25 kez 3m aralıklarla kopyala
pub struct ArrayParams {
    pub direction: Vec3,
    pub spacing: f64,
    pub count: u32,
    pub connect_columns: bool,  // Kopyalar arası kolon bağlantısı
}
```

---

## 6. UNDO/REDO SİSTEMİ (COMMAND PATTERN)

### 6.1 Command Trait

```rust
// src/commands/command.rs

pub trait ModelCommand: Send + Sync + std::fmt::Debug {
    /// Komutu uygula, geri alma verisi döndür
    fn execute(&self, project: &mut Project) -> CommandResult;

    /// Komutu geri al
    fn undo(&self, project: &mut Project) -> CommandResult;

    /// Komut açıklaması (UI'da göstermek için)
    fn description(&self) -> String;
}

pub type CommandResult = Result<(), String>;
```

### 6.2 Undo Stack

```rust
// src/commands/undo_stack.rs

pub struct UndoStack {
    undo_stack: Vec<Box<dyn ModelCommand>>,
    redo_stack: Vec<Box<dyn ModelCommand>>,
    max_size: usize,
}

impl UndoStack {
    pub fn new(max_size: usize) -> Self {
        Self {
            undo_stack: Vec::new(),
            redo_stack: Vec::new(),
            max_size,
        }
    }

    pub fn execute(&mut self, cmd: Box<dyn ModelCommand>, project: &mut Project) -> CommandResult {
        let result = cmd.execute(project);
        if result.is_ok() {
            self.undo_stack.push(cmd);
            self.redo_stack.clear(); // Yeni komut sonrası redo temizlenir
            if self.undo_stack.len() > self.max_size {
                self.undo_stack.remove(0);
            }
        }
        result
    }

    pub fn undo(&mut self, project: &mut Project) -> Option<CommandResult> {
        self.undo_stack.pop().map(|cmd| {
            let result = cmd.undo(project);
            if result.is_ok() {
                self.redo_stack.push(cmd);
            }
            result
        })
    }

    pub fn redo(&mut self, project: &mut Project) -> Option<CommandResult> {
        self.redo_stack.pop().map(|cmd| {
            let result = cmd.execute(project);
            if result.is_ok() {
                self.undo_stack.push(cmd);
            }
            result
        })
    }
}
```

### 6.3 Örnek Komut: Eleman Ekleme

```rust
// src/commands/add_element.rs

#[derive(Debug)]
pub struct AddElementCommand {
    pub element: ElementData,
    pub auto_created_nodes: Vec<NodeData>,  // Otomatik oluşturulan düğümler
}

impl ModelCommand for AddElementCommand {
    fn execute(&self, project: &mut Project) -> CommandResult {
        // Önce gerekli düğümleri ekle
        for node in &self.auto_created_nodes {
            project.nodes.insert(node.id, node.clone());
        }
        // Elemanı ekle
        project.elements.insert(self.element.id, self.element.clone());
        Ok(())
    }

    fn undo(&self, project: &mut Project) -> CommandResult {
        // Elemanı sil
        project.elements.remove(&self.element.id);
        // Otomatik düğümleri sil (başka eleman bağlı değilse)
        for node in &self.auto_created_nodes {
            let has_other_connections = project.elements.values().any(|e| {
                e.node_i == node.id || e.node_j == node.id
            });
            if !has_other_connections {
                project.nodes.remove(&node.id);
            }
        }
        Ok(())
    }

    fn description(&self) -> String {
        format!("Eleman #{} ekle ({:?})", self.element.id, self.element.element_type)
    }
}
```

---

## 7. MATRİS DIŞA AKTARIM (MATRIX EXPORT)

### 7.1 Connectivity Matrix

```rust
// src/io/matrix_export.rs

use csv::Writer;

/// Connectivity matrix: her satır bir eleman, sütunlar [element_id, node_i, node_j, type, length]
pub fn export_connectivity_csv(project: &Project, path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let mut wtr = Writer::from_path(path)?;
    wtr.write_record(&["element_id", "node_i", "node_j", "element_type", "length"])?;

    for elem in project.elements.values() {
        let ni = project.nodes.get(&elem.node_i).unwrap();
        let nj = project.nodes.get(&elem.node_j).unwrap();
        let length = ((nj.x - ni.x).powi(2) + (nj.y - ni.y).powi(2) + (nj.z - ni.z).powi(2)).sqrt();

        wtr.write_record(&[
            elem.id.to_string(),
            elem.node_i.to_string(),
            elem.node_j.to_string(),
            elem.element_type.clone(),
            format!("{:.4}", length),
        ])?;
    }
    wtr.flush()?;
    Ok(())
}
```

### 7.2 Adjacency Matrix (Sparse)

```rust
use nalgebra_sparse::{CooMatrix, CsrMatrix};

/// Adjacency matrix: NxN seyrek matris (N = düğüm sayısı)
pub fn build_adjacency_matrix(project: &Project) -> CsrMatrix<f64> {
    let n = project.nodes.len();
    let mut coo = CooMatrix::new(n, n);

    // Düğüm ID'lerini 0-indexed'e eşle
    let id_to_idx: HashMap<u32, usize> = project.nodes.keys()
        .enumerate()
        .map(|(idx, &id)| (id, idx))
        .collect();

    for elem in project.elements.values() {
        if let (Some(&i), Some(&j)) = (id_to_idx.get(&elem.node_i), id_to_idx.get(&elem.node_j)) {
            coo.push(i, j, 1.0);
            coo.push(j, i, 1.0); // Simetrik
        }
    }

    CsrMatrix::from(&coo)
}

/// Dense format CSV export (mevcut format ile uyumlu)
pub fn export_adjacency_dense_csv(project: &Project, path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let n = project.nodes.len();
    let csr = build_adjacency_matrix(project);

    let mut wtr = Writer::from_path(path)?;
    for i in 0..n {
        let row: Vec<String> = (0..n).map(|j| {
            if csr.get_entry(i, j).is_some() { "1".to_string() } else { "0".to_string() }
        }).collect();
        wtr.write_record(&row)?;
    }
    wtr.flush()?;
    Ok(())
}
```

---

## 8. UI PANEL TASARIMI

### 8.1 Genel Pencere Düzeni

```
+-----------------------------------------------------------------------+
| [Toolbar: File | Edit | View | Draw | Assign | Tools | Help]          |
+----------------+------------------------------------------------------+
| Sol Panel      |                                                      |
| +-----------+  |                                                      |
| | Model     |  |              3D VIEWPORT                            |
| | Ağacı     |  |                                                      |
| | ├ Malzeme |  |    [Wireframe / Extruded / Section Cut]              |
| | │ └ Balsa |  |                                                      |
| | ├ Kesit   |  |         ╱───╲      ╱───╲                            |
| | │ └ 6x6   |  |        │     │    │     │                            |
| | ├ Katlar  |  |        │  A  │────│  B  │   ← İkiz Kule             |
| | │ ├ Kat 0 |  |        │     │    │     │                            |
| | │ ├ Kat 1 |  |         ╲───╱      ╲───╱                            |
| | │ └ ...   |  |                                                      |
| | └ Gruplar |  |    [Orbit: RMB | Pan: MMB | Zoom: Scroll]           |
| +-----------+  |                                                      |
| +-----------+  |                                                      |
| | 2D Kesit  |  |                                                      |
| | Görünümü  |  +------------------------------------------------------+
| |           |  | Alt Panel                                            |
| | [XY|XZ|  |  | Eleman Tablosu / Log / Mesajlar                      |
| |  YZ]      |  | > Model yüklendi: 442 düğüm, 2138 eleman            |
| |  Z:[===]  |  | > Kesit düzlemi: XZ @ Y=8.0, derinlik=2.0          |
| +-----------+  +------------------------------------------------------+
+----------------+ Durum: X=10.0 Y=8.0 Z=45.0 | Snap: Grid+Node | 3 seçili |
+-----------------------------------------------------------------------+
```

### 8.2 Toolbar Detay

```
Dosya:    [Yeni] [Aç] [Kaydet] [Farklı Kaydet] [CSV İçe Aktar] [Dışa Aktar]
Düzenle:  [Geri Al (Ctrl+Z)] [Yinele (Ctrl+Y)] [Kes] [Kopyala] [Yapıştır] [Sil (Del)]
Görünüm:  [Wireframe] [Extruded] [3D] [Plan XY] [Ön XZ] [Yan YZ] [Sığdır (F)]
Çizim:    [Seç (S)] [Kiriş (B)] [Kolon (C)] [Çapraz (X)] [Düğüm (N)]
Atama:    [Kesit] [Malzeme] [Mesnet] [Yük]
Araçlar:  [Taşı (M)] [Kopyala (Ctrl+D)] [Aynala] [Dizi] [Döndür]
Dışa Aktar: [Connectivity CSV] [Adjacency CSV] [OpenSees TCL] [JSON Proje]
```

### 8.3 Sağ Panel — Özellik Düzenleyici

```
+---------------------------+
| ÖZELLİKLER               |
+---------------------------+
| [Hiçbir şey seçili değil]|
| veya                      |
+---------------------------+
| Eleman #1234              |
| Tip: Column               |
| ├ Düğüm I: 42            |
| │  X: 5.00  Y: 8.00      |
| │  Z: 0.00               |
| ├ Düğüm J: 85            |
| │  X: 5.00  Y: 8.00      |
| │  Z: 6.00               |
| ├ Uzunluk: 6.000         |
| ├ Kesit: [6x6 Balsa ▼]   |
| ├ Malzeme: [Balsa ▼]     |
| ├ I-ucu Serbest:         |
| │  □Ux □Uy □Uz           |
| │  □Rx □Ry □Rz           |
| ├ J-ucu Serbest:         |
| │  □Ux □Uy □Uz           |
| │  □Rx □Ry □Rz           |
| └ Renk: [■ Kırmızı]     |
+---------------------------+
| [Uygula] [Seçime Ata]    |
+---------------------------+
```

---

## 9. KLAVYE KISAYOLLARI

| Kısayol | İşlem |
|---------|-------|
| `S` | Seçim modu |
| `B` | Kiriş çizim modu |
| `C` | Kolon çizim modu |
| `X` | Çapraz çizim modu |
| `N` | Düğüm oluşturma modu |
| `M` | Taşıma modu |
| `Ctrl+D` | Seçili elemanları kopyala |
| `Ctrl+Z` | Geri al |
| `Ctrl+Y` | Yinele |
| `Ctrl+A` | Tümünü seç |
| `Del` | Seçili elemanları sil |
| `Esc` | Seçimi/aracı iptal et |
| `F` | Modele sığdır (zoom fit) |
| `1` | Plan görünümü (XY) |
| `2` | Ön görünüş (XZ) |
| `3` | Yan görünüş (YZ) |
| `4` | 3D perspektif |
| `5` | Ortografik/perspektif geçişi |
| `G` | Grid göster/gizle |
| `L` | Label göster/gizle |
| `E` | Extruded section geçişi |
| `Tab` | Sürekli çizim modu geçişi |
| `Ctrl+S` | Kaydet |
| `Ctrl+O` | Aç |
| `Ctrl+Shift+E` | Connectivity matrix export |
| `Shift+Seç` | Seçime ekle |
| `Ctrl+Seç` | Seçimden çıkar/ekle (toggle) |

---

## 10. GELİŞTİRME AŞAMALARI (PHASES)

### Faz 1 — Minimum Uygulanabilir Ürün (MVP) — ~4 hafta

**Hedef:** Mevcut DASK modelini yükleyip 3D'de interaktif olarak görüntüleme

| # | Görev | Süre |
|---|-------|------|
| 1.1 | Cargo projesi oluştur, Bevy + bevy_egui + bevy_panorbit_camera kurulumu | 1 gün |
| 1.2 | `model/` modülünü yaz: Node, Element, Project struct'ları | 2 gün |
| 1.3 | CSV import: `position_matrix.csv` ve `connectivity_matrix.csv` okuma | 1 gün |
| 1.4 | ECS spawn: düğümleri küçük küre, elemanları renkli çizgi olarak 3D sahneye ekle | 2 gün |
| 1.5 | Kamera kurulumu: orbit, pan, zoom (bevy_panorbit_camera) | 1 gün |
| 1.6 | Grid çizimi: XY ve XZ düzlemlerinde referans grid | 1 gün |
| 1.7 | Temel egui panelleri: toolbar (boş), sol panel (model ağacı basit), durum çubuğu | 2 gün |
| 1.8 | Element tıklama seçimi (Bevy picking) + renk değişimi | 2 gün |
| 1.9 | Sağ panel: seçili eleman özelliklerini göster (salt okunur) | 1 gün |
| 1.10 | Görünüm geçişleri: Plan (1), Ön (2), Yan (3), 3D (4) | 1 gün |
| 1.11 | Eleman tipine göre renklendirme + renk legend | 1 gün |

**Çıktı:** 3D'de döndürülebilen, elemanları seçilebilen, özellik panelli yapısal model görüntüleyici.

### Faz 2 — Kesit Düzlemleri + 2D Görünüm — ~3 hafta

| # | Görev | Süre |
|---|-------|------|
| 2.1 | `SectionPlanes` resource ve egui slider kontrolleri | 1 gün |
| 2.2 | WGSL section cut shader (fragment discard) | 3 gün |
| 2.3 | Bevy custom material entegrasyonu | 2 gün |
| 2.4 | Yarı saydam kesit düzlemi mesh'i 3D'de göster | 1 gün |
| 2.5 | Geometrik kesit çıkartma (2D projeksiyon) nalgebra ile | 2 gün |
| 2.6 | Sol panelde 2D kesit görünümü (egui canvas ile çizim) | 3 gün |
| 2.7 | View depth kontrolü (slider) | 1 gün |
| 2.8 | Kat bazlı navigasyon: dropdown ile kat seçimi → XY plane ayarı | 1 gün |
| 2.9 | Kesit görünümünde eleman renklendirme ve hover bilgisi | 1 gün |

**Çıktı:** Sol panelde 2D kesit görünümleri, sağda kırpılan 3D model, slider'larla interaktif düzlem kontrolü.

### Faz 3 — İnteraktif Element Çizimi — ~3 hafta

| # | Görev | Süre |
|---|-------|------|
| 3.1 | `ToolMode` state machine ve toolbar buton entegrasyonu | 1 gün |
| 3.2 | Snap sistemi: düğüm snap + grid snap | 2 gün |
| 3.3 | Kiriş çizim modu: ilk tık → ikinci tık → eleman oluştur | 2 gün |
| 3.4 | Kolon çizim modu (aynı mantık, farklı tip) | 0.5 gün |
| 3.5 | Çapraz çizim modu | 0.5 gün |
| 3.6 | Preview çizgi: çizim sırasında noktalı çizgi gösterimi | 1 gün |
| 3.7 | Sürekli çizim modu (Tab ile toggle) | 1 gün |
| 3.8 | Düğüm oluşturma modu (koordinat girişi dialogu) | 1 gün |
| 3.9 | Undo/Redo sistemi: Command trait, UndoStack | 2 gün |
| 3.10 | AddElement, AddNode, DeleteElements komutları | 2 gün |
| 3.11 | Silme işlemi: seçili elemanları sil (orphan düğüm temizliği dahil) | 1 gün |

**Çıktı:** 3D sahne üzerinde interaktif element çizebilen, geri alınabilen modelleme aracı.

### Faz 4 — Dönüştürme ve Düzenleme — ~2 hafta

| # | Görev | Süre |
|---|-------|------|
| 4.1 | Düğüm taşıma: seçili düğümleri dx, dy, dz kadar kaydır | 2 gün |
| 4.2 | Eleman kopyalama: seçili elemanları offset ile çoğalt | 2 gün |
| 4.3 | Linear array: N kopya, eşit aralık | 1 gün |
| 4.4 | Mirror: XY, XZ, YZ düzlemlerinde aynalama | 2 gün |
| 4.5 | Window select: sola çek → içindekiler, sağa çek → kesişenler | 2 gün |
| 4.6 | Tip filtreli seçim: sadece kolon / sadece kiriş seç | 1 gün |
| 4.7 | MoveNodes, CopyElements, MirrorElements undo komutları | 2 gün |

**Çıktı:** Tam düzenleme yetenekli yapısal modelleme aracı.

### Faz 5 — Kesit & Malzeme Atama + Dışa Aktarım — ~2 hafta

| # | Görev | Süre |
|---|-------|------|
| 5.1 | Kesit tanımlama dialogu: dikdörtgen, I-profil, daire, boru | 2 gün |
| 5.2 | Kesit önizleme (egui canvas'da çizim) | 1 gün |
| 5.3 | Malzeme tanımlama dialogu | 1 gün |
| 5.4 | Kesit/malzeme atama: seçili elemanlara ata | 1 gün |
| 5.5 | Extruded section görünümü (kesit profili mesh üretimi) | 3 gün |
| 5.6 | Connectivity matrix CSV export | 1 gün |
| 5.7 | Adjacency matrix CSV export (dense + sparse) | 1 gün |
| 5.8 | JSON proje dosyası kaydet/yükle | 1 gün |
| 5.9 | OpenSees TCL export (bonus) | 2 gün |

**Çıktı:** Kesit atanabilen, matris dışa aktarılabilen, proje kaydedilebilen tam uygulama.

### Faz 6 — Cilalama ve İleri Özellikler — ~2 hafta

| # | Görev | Süre |
|---|-------|------|
| 6.1 | Model doğrulama: orphan düğüm, sıfır uzunluklu eleman, eksik kesit uyarısı | 2 gün |
| 6.2 | Mesnet (restraint) atama dialogu (6 DOF checkbox) | 1 gün |
| 6.3 | Düğüm birleştirme (merge joints): tolerans mesafesi ile | 1 gün |
| 6.4 | Eleman tablosu paneli (alt panel): sıralanabilir, filtrelenebilir tablo | 2 gün |
| 6.5 | Label gösterimi: düğüm/eleman numarası overlay | 1 gün |
| 6.6 | Renk modu seçimi: tipe göre / kesite göre / kata göre | 1 gün |
| 6.7 | İkon tasarımı ve tema (koyu mod) | 1 gün |
| 6.8 | Performans optimizasyonu: instanced rendering, LOD | 2 gün |
| 6.9 | Türkçe lokalizasyon (tüm UI metinleri) | 1 gün |

---

## 11. WSL2 GELİŞTİRME ORTAMI KURULUMU

### 11.1 Ön Gereksinimler

```bash
# WSL2 Ubuntu'da
sudo apt update && sudo apt upgrade -y

# Rust kurulumu
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
rustup update

# Bevy bağımlılıkları (WSL2 + wayland/x11)
sudo apt install -y \
    g++ pkg-config libx11-dev libxi-dev libxcursor-dev \
    libxrandr-dev libxinerama-dev libgl1-mesa-dev \
    libasound2-dev libudev-dev libwayland-dev \
    libxkbcommon-dev vulkan-tools mesa-vulkan-drivers

# WSLg GPU desteği kontrolü
glxinfo | grep "OpenGL version"
vulkaninfo --summary
```

### 11.2 Proje Oluşturma

```bash
cd /mnt/c/Users/lenovo/Desktop/DASK_NEW
cargo new dask-modeler
cd dask-modeler

# Cargo.toml düzenle (Bölüm 2.6'daki içerik)
# İlk derleme (~5-10 dk, Bevy büyük)
cargo build
```

### 11.3 WSL2 GPU İpuçları

```bash
# WSLg ile Bevy GUI doğrudan çalışır (Windows 11)
# Eğer GPU sorunları varsa:
export WGPU_BACKEND=gl       # OpenGL fallback
# veya
export WGPU_BACKEND=vulkan   # Vulkan (tercih edilen)

# Çalıştırma
cargo run
```

---

## 12. PERFORMANS HEDEFLERİ

| Metrik | Hedef | Gerekçe |
|--------|-------|---------|
| FPS (3D viewport) | ≥ 60 fps | 2138 çizgi + 442 küre trivial |
| İlk yükleme | < 2 sn | CSV parse + ECS spawn |
| Eleman seçimi | < 16 ms | Raycast tek frame içinde |
| Undo/Redo | < 1 ms | HashMap insert/remove |
| CSV export | < 100 ms | 2138 satır yazma |
| Adjacency matrix | < 500 ms | 442×442 dense yazma |
| Bellek kullanımı | < 200 MB | Model verisi ~10 MB + GPU buffer'lar |
| İlk derleme | ~5-10 dk | Bevy dependency tree |
| Artımlı derleme | < 10 sn | Sadece değişen modüller |

---

## 13. TEST STRATEJİSİ

### 13.1 Unit Testler

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_position_csv() {
        let project = Project::from_csv(
            "test_data/position_matrix.csv",
            "test_data/connectivity_matrix.csv",
        ).unwrap();
        assert_eq!(project.nodes.len(), 442);
        assert_eq!(project.elements.len(), 2138);
    }

    #[test]
    fn test_adjacency_matrix_symmetric() {
        let project = create_test_project();
        let adj = build_adjacency_matrix(&project);
        // Simetri kontrolü
        for (i, j, v) in adj.triplet_iter() {
            assert_eq!(adj.get(j, i), Some(v));
        }
    }

    #[test]
    fn test_section_plane_intersection() {
        let plane = ClipPlane {
            normal: Vector3::new(0.0, 0.0, 1.0),
            point: Point3::new(0.0, 0.0, 50.0),
        };
        let a = Point3::new(5.0, 8.0, 0.0);
        let b = Point3::new(5.0, 8.0, 100.0);

        let intersection = plane.intersect_segment(&a, &b).unwrap();
        assert!((intersection.z - 50.0).abs() < 1e-10);
    }

    #[test]
    fn test_undo_redo_add_element() {
        let mut project = create_test_project();
        let mut stack = UndoStack::new(100);

        let initial_count = project.elements.len();
        let cmd = Box::new(AddElementCommand { /* ... */ });
        stack.execute(cmd, &mut project).unwrap();
        assert_eq!(project.elements.len(), initial_count + 1);

        stack.undo(&mut project);
        assert_eq!(project.elements.len(), initial_count);

        stack.redo(&mut project);
        assert_eq!(project.elements.len(), initial_count + 1);
    }
}
```

### 13.2 Entegrasyon Testleri

- CSV import → export round-trip: orijinal dosyayla karşılaştır
- JSON proje kaydet → yükle round-trip: tüm veri korunuyor mu
- Adjacency matrix: 442×442 boyut, doğru bağlantı sayısı (2138×2 = 4276 non-zero)
- Section cut: bilinen geometride beklenen kesişim noktaları

---

## 14. REFERANSLAR

### Rust Crate'leri
- [Bevy Engine](https://bevyengine.org/) — v0.17, ECS oyun motoru
- [bevy_egui](https://github.com/mvlabat/bevy_egui) — Bevy + egui entegrasyonu
- [bevy_panorbit_camera](https://github.com/Plonq/bevy_panorbit_camera) — Orbit kamera
- [egui](https://github.com/emilk/egui) — Immediate-mode GUI
- [nalgebra](https://nalgebra.org/) — Lineer cebir kütüphanesi
- [nalgebra-sparse](https://docs.rs/nalgebra-sparse/) — Seyrek matrisler
- [serde](https://serde.rs/) — Serialization framework
- [csv](https://github.com/BurntSushi/rust-csv) — CSV parser

### Yapısal Mühendislik Referansları
- SAP2000 v25 User Manual — CSI Berkeley
- Tekla Structures 2024 — Trimble
- TBDY 2018 — Türk Bina Deprem Yönetmeliği
- DASK 2026 Yarışma Şartnamesi

### Teknik Kaynaklar
- [WGSL Specification](https://www.w3.org/TR/WGSL/) — WebGPU Shading Language
- [Fragment Discard Clipping](https://prideout.net/clip-planes) — Shader-based section cutting
- [Command Pattern](https://refactoring.guru/design-patterns/command) — Undo/Redo implementasyonu
- [ECS Architecture](https://www.flecs.dev/flecs/md_docs_2Entities.html) — Entity-Component-System

---

## 15. SONUÇ

Bu plan, SAP2000 ve Tekla Structures'ın temel özelliklerini Rust + Bevy + egui yığını ile
yeniden üreten bir yapısal modelleme uygulaması için kapsamlı bir yol haritası sunmaktadır.

**Toplam tahmini geliştirme süresi: ~16 hafta (4 ay)**

Projenin en kritik avantajı, mevcut DASK 2026 veri dosyalarıyla (position_matrix.csv,
connectivity_matrix.csv) doğrudan entegre olması ve OpenSees TCL dosya çıktısı üretebilmesidir.

Bevy ECS mimarisi, her yapısal elemanı bir entity olarak modellemekle kalmayıp paralel
sistemler sayesinde binlerce elemanlı modellerde bile 60+ FPS rendering performansı
sunacaktır. Fragment shader tabanlı section cutting, nalgebra ile geometrik kesit çıkartma
ve egui immediate-mode GUI'nin birleşimi; profesyonel düzeyde bir 3D yapısal modelleme
deneyimi sağlayacaktır.

## 16. IMPLEMENTATION NOTES (2026-02-28)

- **Windows 11 Native Build** validated using Visual Studio 2022 Build Tools (MSVC) and Rust stable `x86_64-pc-windows-msvc`.
- **Dependency alignment decision:** `bevy_panorbit_camera` was updated from `0.25` to `0.33.x` to match `bevy 0.17` and avoid mixed Bevy major/minor versions at runtime.
- **Phase 1 scope status:** core scaffolding, ECS/data model, CSV import/tests, gizmo rendering, basic egui panels, element selection, and view presets are implemented and compiling on Windows.
- **Phase 2 implementation (2026-02-28):** section-plane controls, section clipping material/shader, plane visual quads, nalgebra-based section extraction, and 2D section panel were added.
- **bevy_egui scheduling fix:** UI systems are scheduled on `EguiPrimaryContextPass` (not `Update`) to avoid runtime `available_rect()` panics.
- **Phase 3 implementation (2026-02-28):** tool-mode drawing workflow, snap+preview line, coordinate-input dialog, command-based undo/redo (add node/element, delete elements), continuous draw mode, and delete-orphan-node cleanup were added.
- **Model opener added:** toolbar dataset selector scans `data/` for `*position_matrix*.csv` + matching `*connectivity_matrix*.csv` pairs (including `v10` variants) and reloads selected models at runtime.
- **Startup behavior change (2026-02-28):** application now opens as an empty workspace (no auto-loaded model). Models load only via toolbar `Open Model`.
- **Phase 4 core implementation (2026-02-28):** added undoable `MoveNodesCommand`, `CopyElementsCommand` (single + linear array), and `MirrorElementsCommand`; added transform dialogs, keyboard shortcuts, drag-move mode, preview overlays, window selection (LTR inside / RTL crossing), and type-filtered element selection.
- **File/Open workflow (2026-02-28):** added native Windows file dialog support (`rfd`) for opening arbitrary CSV pairs and JSON project files, including a recent-files list in toolbar.
- **File menu enhancements (2026-02-28):** added `New Model`, `Save JSON`, and `Save JSON As...` actions with active project path tracking and recent-file updates.
- **Phase 5 implementation (2026-02-28):** added section/material creation dialogs, command-based section/material assignment on selected elements, connectivity/adjacency matrix export (dense + sparse CSR), and OpenSees TCL export via File menu.
- **Phase 5 addendum (2026-02-28):** element mesh thickness now derives from assigned section geometry, providing basic extruded member visualization during 3D rendering.
- **Phase 6 implementation (2026-02-28):** added model validation reporting (orphan nodes, zero-length, missing section), restraint assignment dialog (6 DOF) with undo command support, node merge command with tolerance, element table panel (filter/sort), screen-space node/element label overlays, render color modes by section/material/floor, restraint triangle markers, simple LOD distance culling, dark-theme controls, and Turkish-first UI labels.
- **Phase 6 render addendum (2026-02-28):** node gizmo spheres were replaced with shared-mesh node entities (Sphere + shared StandardMaterial) so Bevy can batch/instance node rendering on GPU; node visibility now follows show_nodes, node-size scaling, and camera-distance LOD.
- **UI consistency pass (2026-02-28):** Turkish labels were normalized in toolbar/dialog/table controls and Windows file dialog filters.
