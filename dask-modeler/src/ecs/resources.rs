//! ECS resources for global editor/application state.

use std::path::PathBuf;

use bevy::prelude::*;

use crate::ecs::components::ElementType;
use crate::model::Project;

/// Active editor tool.
#[derive(Resource, Default, PartialEq, Eq, Clone, Copy)]
pub enum ToolMode {
    #[default]
    Select,
    DrawBeam,
    DrawColumn,
    DrawBrace,
    MoveNode,
    Pan,
}

/// Camera preset/view mode metadata.
#[derive(Resource, Default, PartialEq, Eq, Clone, Copy)]
pub enum ViewMode {
    #[default]
    View3D,
    Plan,
    Front,
    Side,
}

/// Section cutting planes state.
#[derive(Resource)]
pub struct SectionPlanes {
    pub xy_enabled: bool,
    pub xy_z: f32,
    pub xz_enabled: bool,
    pub xz_y: f32,
    pub yz_enabled: bool,
    pub yz_x: f32,
    pub depth: f32,
    pub floor_navigation: Option<u32>,
}

impl Default for SectionPlanes {
    fn default() -> Self {
        Self {
            xy_enabled: false,
            xy_z: 0.0,
            xz_enabled: false,
            xz_y: 8.0,
            yz_enabled: false,
            yz_x: 10.0,
            depth: 1.0,
            floor_navigation: None,
        }
    }
}

/// Element coloring mode.
#[derive(Default, PartialEq, Eq, Clone, Copy)]
pub enum ColorMode {
    #[default]
    ByElementType,
    BySection,
    ByMaterial,
    ByFloor,
    Uniform,
}

/// Display/rendering settings.
#[derive(Resource)]
pub struct DisplaySettings {
    pub show_nodes: bool,
    pub show_labels: bool,
    pub show_grid: bool,
    pub show_axes: bool,
    pub show_restraints: bool,
    pub show_extruded: bool,
    pub show_local_axes: bool,
    pub show_releases: bool,
    pub color_mode: ColorMode,
    pub grid_spacing: f32,
    pub node_size: f32,
    pub line_width: f32,
    pub lod_distance: f32,
}

impl Default for DisplaySettings {
    fn default() -> Self {
        Self {
            show_nodes: true,
            show_labels: false,
            show_grid: true,
            show_axes: true,
            show_restraints: true,
            show_extruded: false,
            show_local_axes: false,
            show_releases: false,
            color_mode: ColorMode::ByElementType,
            grid_spacing: 1.0,
            node_size: 0.15,
            line_width: 2.0,
            lod_distance: 800.0,
        }
    }
}

/// Snapping behavior settings.
#[derive(Resource)]
pub struct SnapSettings {
    pub snap_to_grid: bool,
    pub snap_to_node: bool,
    pub snap_to_midpoint: bool,
    pub snap_distance: f32,
    pub grid_snap_size: f32,
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

/// Interactive drawing workflow state.
#[derive(Resource, Default)]
pub struct DrawingState {
    pub first_node: Option<u32>,
    pub preview_end: Option<Vec3>,
    pub continuous: bool,
    pub element_type: ElementType,
}

/// Current selection metadata.
#[derive(Resource, Default)]
pub struct SelectionState {
    pub selected_nodes: Vec<u32>,
    pub selected_elements: Vec<u32>,
    pub box_select_start: Option<Vec2>,
    pub box_select_end: Option<Vec2>,
}

/// Model-level stats shown in status UI.
#[derive(Resource, Default)]
pub struct ModelStats {
    pub total_nodes: usize,
    pub total_elements: usize,
    pub total_dofs: usize,
    pub selected_count: usize,
    pub cursor_world_pos: Vec3,
}

/// Floor/type filtering used by model-tree UI.
#[derive(Resource, Default)]
pub struct VisibilityFilter {
    pub floor: Option<u32>,
    pub element_type: Option<ElementType>,
}

/// Loaded project data mirrored into ECS resources.
#[derive(Resource, Clone, Debug, Default)]
pub struct ProjectResource {
    pub project: Project,
}

/// Dataset metadata used by the model opener.
#[derive(Clone, Debug, Default)]
pub struct ModelDataset {
    pub label: String,
    pub position_csv: PathBuf,
    pub connectivity_csv: PathBuf,
}

/// Available datasets and current selection for quick model loading.
#[derive(Resource, Clone, Debug, Default)]
pub struct ModelCatalog {
    pub datasets: Vec<ModelDataset>,
    pub selected_index: usize,
    pub load_requested: bool,
}

/// File-based model open request kinds.
#[derive(Clone, Debug)]
pub enum FileOpenRequest {
    CsvPair {
        position_csv: PathBuf,
        connectivity_csv: PathBuf,
    },
    JsonProject {
        path: PathBuf,
    },
}

/// File-based export request kinds.
#[derive(Clone, Debug)]
pub enum ExportRequest {
    ConnectivityCsv { path: PathBuf },
    AdjacencyDenseCsv { path: PathBuf },
    AdjacencySparseCsrCsv { path: PathBuf },
    OpenSeesTcl { path: PathBuf },
}

/// Recent model entry metadata.
#[derive(Clone, Debug)]
pub struct RecentModelEntry {
    pub label: String,
    pub request: FileOpenRequest,
}

/// State used by file-open dialogs and pending model load requests.
#[derive(Resource, Clone, Debug, Default)]
pub struct FileDialogState {
    pub pending_open: Option<FileOpenRequest>,
    pub pending_save: Option<PathBuf>,
    pub pending_export: Option<ExportRequest>,
    pub new_model_requested: bool,
    pub active_json_path: Option<PathBuf>,
    pub recent: Vec<RecentModelEntry>,
    pub last_directory: Option<PathBuf>,
}

/// Indicates that ECS entities should be rebuilt from `ProjectResource`.
#[derive(Resource, Clone, Copy, Debug, Default)]
pub struct ModelChangeState {
    pub dirty: bool,
}

/// Coordinate-input dialog state for precise node placement.
#[derive(Resource, Clone, Debug)]
pub struct CoordinateInputState {
    pub open: bool,
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

impl Default for CoordinateInputState {
    fn default() -> Self {
        Self {
            open: false,
            x: 0.0,
            y: 0.0,
            z: 0.0,
        }
    }
}

/// Selectability filter by element type.
#[derive(Resource, Clone, Debug)]
pub struct SelectionTypeFilter {
    pub beam_x: bool,
    pub beam_y: bool,
    pub column: bool,
    pub brace_xz: bool,
    pub brace_yz: bool,
    pub brace_floor: bool,
    pub core_wall: bool,
    pub chevron: bool,
    pub brace_space: bool,
    pub custom: bool,
}

impl Default for SelectionTypeFilter {
    fn default() -> Self {
        Self {
            beam_x: true,
            beam_y: true,
            column: true,
            brace_xz: true,
            brace_yz: true,
            brace_floor: true,
            core_wall: true,
            chevron: true,
            brace_space: true,
            custom: true,
        }
    }
}

impl SelectionTypeFilter {
    /// Returns whether selection is enabled for a given element type.
    pub fn allows(&self, kind: &ElementType) -> bool {
        match kind {
            ElementType::BeamX => self.beam_x,
            ElementType::BeamY => self.beam_y,
            ElementType::Column => self.column,
            ElementType::BraceXZ => self.brace_xz,
            ElementType::BraceYZ => self.brace_yz,
            ElementType::BraceFloor => self.brace_floor,
            ElementType::CoreWall => self.core_wall,
            ElementType::Chevron => self.chevron,
            ElementType::BraceSpace => self.brace_space,
            ElementType::Custom(_) => self.custom,
        }
    }
}

/// Transform operation dialog and preview state.
#[derive(Resource, Clone, Debug)]
pub struct TransformOpsState {
    pub move_open: bool,
    pub copy_open: bool,
    pub array_open: bool,
    pub mirror_open: bool,
    pub move_apply_requested: bool,
    pub copy_apply_requested: bool,
    pub array_apply_requested: bool,
    pub mirror_apply_requested: bool,
    pub move_dx: f64,
    pub move_dy: f64,
    pub move_dz: f64,
    pub copy_dx: f64,
    pub copy_dy: f64,
    pub copy_dz: f64,
    pub array_dx: f64,
    pub array_dy: f64,
    pub array_dz: f64,
    pub array_count: u32,
    pub mirror_plane: crate::commands::mirror_elements::MirrorPlane,
    pub mirror_position: f64,
    pub drag_move_active: bool,
    pub drag_origin: Option<Vec3>,
}

impl Default for TransformOpsState {
    fn default() -> Self {
        Self {
            move_open: false,
            copy_open: false,
            array_open: false,
            mirror_open: false,
            move_apply_requested: false,
            copy_apply_requested: false,
            array_apply_requested: false,
            mirror_apply_requested: false,
            move_dx: 0.0,
            move_dy: 0.0,
            move_dz: 0.0,
            copy_dx: 1.0,
            copy_dy: 0.0,
            copy_dz: 0.0,
            array_dx: 0.0,
            array_dy: 0.0,
            array_dz: 6.0,
            array_count: 3,
            mirror_plane: crate::commands::mirror_elements::MirrorPlane::YZ,
            mirror_position: 0.0,
            drag_move_active: false,
            drag_origin: None,
        }
    }
}

/// Parametric section shape selector used by the new-section dialog.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub enum SectionShapeKind {
    #[default]
    Rectangular,
    IBeam,
    Circular,
    Pipe,
    LAngle,
}

/// Dialog state for creating a section definition.
#[derive(Resource, Clone, Debug)]
pub struct NewSectionDialogState {
    pub open: bool,
    pub name: String,
    pub shape: SectionShapeKind,
    pub width: f64,
    pub height: f64,
    pub flange_w: f64,
    pub flange_t: f64,
    pub web_h: f64,
    pub web_t: f64,
    pub diameter: f64,
    pub outer_d: f64,
    pub inner_d: f64,
    pub leg_a: f64,
    pub leg_b: f64,
    pub thickness: f64,
    pub color: [f32; 3],
}

impl Default for NewSectionDialogState {
    fn default() -> Self {
        Self {
            open: false,
            name: "SEC-1".to_string(),
            shape: SectionShapeKind::Rectangular,
            width: 6.0,
            height: 6.0,
            flange_w: 6.0,
            flange_t: 0.8,
            web_h: 4.4,
            web_t: 0.6,
            diameter: 6.0,
            outer_d: 6.0,
            inner_d: 4.0,
            leg_a: 6.0,
            leg_b: 6.0,
            thickness: 0.6,
            color: [0.65, 0.65, 0.65],
        }
    }
}

/// Dialog state for creating a material definition.
#[derive(Resource, Clone, Debug)]
pub struct NewMaterialDialogState {
    pub open: bool,
    pub name: String,
    pub e: f64,
    pub g: f64,
    pub nu: f64,
    pub density: f64,
    pub fy: f64,
    pub fu: f64,
}

impl Default for NewMaterialDialogState {
    fn default() -> Self {
        Self {
            open: false,
            name: "Balsa".to_string(),
            e: 3500.0,
            g: 1346.0,
            nu: 0.3,
            density: 160.0,
            fy: 0.0,
            fu: 0.0,
        }
    }
}

/// Dialog state for node restraint assignment.
#[derive(Resource, Clone, Debug)]
pub struct RestraintDialogState {
    pub open: bool,
    pub ux: bool,
    pub uy: bool,
    pub uz: bool,
    pub rx: bool,
    pub ry: bool,
    pub rz: bool,
    pub apply_requested: bool,
}

impl Default for RestraintDialogState {
    fn default() -> Self {
        Self {
            open: false,
            ux: true,
            uy: true,
            uz: true,
            rx: true,
            ry: true,
            rz: true,
            apply_requested: false,
        }
    }
}

/// Node-merge operation state.
#[derive(Resource, Clone, Debug)]
pub struct NodeMergeState {
    pub tolerance: f64,
    pub merge_requested: bool,
}

impl Default for NodeMergeState {
    fn default() -> Self {
        Self {
            tolerance: 0.1,
            merge_requested: false,
        }
    }
}

/// UI theme and localization settings.
#[derive(Resource, Clone, Debug)]
pub struct UiSettings {
    pub dark_theme: bool,
    pub turkish: bool,
}

impl Default for UiSettings {
    fn default() -> Self {
        Self {
            dark_theme: true,
            turkish: true,
        }
    }
}

/// Element-table view state.
#[derive(Resource, Clone, Debug)]
pub struct ElementTableState {
    pub show: bool,
    pub filter_text: String,
    pub sort_by: ElementTableSortBy,
    pub ascending: bool,
}

impl Default for ElementTableState {
    fn default() -> Self {
        Self {
            show: true,
            filter_text: String::new(),
            sort_by: ElementTableSortBy::Id,
            ascending: true,
        }
    }
}

/// Sort key for the element table.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub enum ElementTableSortBy {
    #[default]
    Id,
    Type,
    Length,
    NodeI,
    NodeJ,
}
