//! Application entry point for the DASK structural modeler.

use std::fs;
use std::path::PathBuf;

use bevy::pbr::{MaterialPlugin, StandardMaterial};
use bevy::picking::prelude::{MeshPickingCamera, MeshPickingPlugin, Pickable};
use bevy::prelude::*;
use bevy_egui::{EguiPlugin, EguiPrimaryContextPass};
use bevy_panorbit_camera::{PanOrbitCamera, PanOrbitCameraPlugin};
use dask_modeler::commands::{AssignRestraintsCommand, MergeNodesCommand, UndoStack};
use dask_modeler::ecs::components::{
    ElementMarker, NodeMarker, NodeZone, StructuralElement, StructuralNode,
};
use dask_modeler::ecs::events::SelectionChangedEvent;
use dask_modeler::ecs::resources::{
    CoordinateInputState, DisplaySettings, DrawingState, ElementTableState, ExportRequest,
    FileDialogState, FileOpenRequest, ModelCatalog, ModelChangeState, ModelDataset, ModelStats,
    NewMaterialDialogState, NewSectionDialogState, NodeMergeState, ProjectResource,
    RestraintDialogState, SectionPlanes, SelectionState, SelectionTypeFilter, SnapSettings,
    ToolMode, TransformOpsState, UiSettings, ViewMode, VisibilityFilter,
};
use dask_modeler::ecs::systems::camera::{MainCamera, apply_view_mode, keyboard_view_presets};
use dask_modeler::ecs::systems::drawing::{
    cancel_drawing_with_escape, draw_snap_and_preview, handle_drawing_clicks,
    handle_edit_shortcuts, sync_tool_mode_to_drawing_state, toggle_continuous_draw,
};
use dask_modeler::ecs::systems::grid::draw_reference_grids;
use dask_modeler::ecs::systems::input::update_cursor_world_position;
use dask_modeler::ecs::systems::picking::handle_element_click_selection;
use dask_modeler::ecs::systems::render::{draw_structural_model, sync_node_visuals};
use dask_modeler::ecs::systems::section_cut::{
    SectionCutMaterial, section_plane_shortcuts, spawn_section_plane_visuals,
    sync_section_cut_materials, update_section_plane_visuals,
};
use dask_modeler::ecs::systems::transform::{
    apply_transform_requests, draw_transform_previews, handle_node_drag_move,
    handle_transform_shortcuts, handle_window_selection,
};
use dask_modeler::io::json_project::{load_project_json, save_project_json};
use dask_modeler::io::matrix_export::{
    export_adjacency_dense_csv, export_adjacency_sparse_csr_csv, export_connectivity_csv,
};
use dask_modeler::io::opensees_export::export_opensees_tcl;
use dask_modeler::model::Project;
use dask_modeler::ui::dialogs::coordinate_input::coordinate_input_dialog_ui;
use dask_modeler::ui::dialogs::new_material::new_material_dialog_ui;
use dask_modeler::ui::dialogs::new_section::new_section_dialog_ui;
use dask_modeler::ui::dialogs::restraint_assignment::restraint_assignment_dialog_ui;
use dask_modeler::ui::element_table::element_table_ui;
use dask_modeler::ui::labels_overlay::labels_overlay_ui;
use dask_modeler::ui::model_tree::model_tree_ui;
use dask_modeler::ui::properties_panel::properties_panel_ui;
use dask_modeler::ui::section_plane_controls::section_plane_controls_ui;
use dask_modeler::ui::section_view::section_view_ui;
use dask_modeler::ui::status_bar::status_bar_ui;
use dask_modeler::ui::theme::apply_ui_theme;
use dask_modeler::ui::toolbar::toolbar_ui;
use log::{error, info};

const DEFAULT_CENTER: Vec3 = Vec3::new(10.0, 8.0, 76.0);
const DEFAULT_EYE: Vec3 = Vec3::new(90.0, 65.0, 110.0);

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugins(EguiPlugin::default())
        .add_plugins(PanOrbitCameraPlugin)
        .add_plugins(MaterialPlugin::<SectionCutMaterial>::default())
        .add_plugins(MeshPickingPlugin)
        .insert_resource(ToolMode::default())
        .insert_resource(ViewMode::default())
        .insert_resource(SectionPlanes::default())
        .insert_resource(DisplaySettings::default())
        .insert_resource(SnapSettings::default())
        .insert_resource(DrawingState::default())
        .insert_resource(SelectionState::default())
        .insert_resource(CoordinateInputState::default())
        .insert_resource(NewSectionDialogState::default())
        .insert_resource(NewMaterialDialogState::default())
        .insert_resource(RestraintDialogState::default())
        .insert_resource(NodeMergeState::default())
        .insert_resource(UiSettings::default())
        .insert_resource(ElementTableState::default())
        .insert_resource(ModelStats::default())
        .insert_resource(VisibilityFilter::default())
        .insert_resource(ModelCatalog::default())
        .insert_resource(FileDialogState::default())
        .insert_resource(ModelChangeState::default())
        .insert_resource(ProjectResource::default())
        .insert_resource(SelectionTypeFilter::default())
        .insert_resource(TransformOpsState::default())
        .insert_resource(UndoStack::default())
        .add_message::<SelectionChangedEvent>()
        .add_systems(
            Startup,
            (
                setup_scene,
                initialize_model_catalog,
                spawn_section_plane_visuals,
            ),
        )
        .add_systems(
            Update,
            (
                keyboard_view_presets,
                apply_view_mode,
                section_plane_shortcuts,
                update_cursor_world_position,
                handle_transform_shortcuts,
                handle_window_selection,
                handle_element_click_selection,
                handle_node_drag_move,
                apply_transform_requests,
                sync_tool_mode_to_drawing_state,
                toggle_continuous_draw,
                cancel_drawing_with_escape,
                handle_drawing_clicks,
                handle_edit_shortcuts,
                handle_file_menu_actions,
                handle_model_edit_requests,
                load_model_from_file_dialog,
            ),
        )
        .add_systems(
            Update,
            (
                load_selected_model_from_catalog,
                rebuild_model_entities_if_dirty,
                sync_section_cut_materials,
                update_section_plane_visuals,
                draw_reference_grids,
                sync_node_visuals,
                draw_structural_model,
                draw_transform_previews,
                draw_snap_and_preview,
            ),
        )
        .add_systems(
            EguiPrimaryContextPass,
            (
                toolbar_ui,
                model_tree_ui,
                section_plane_controls_ui,
                section_view_ui,
                properties_panel_ui,
                status_bar_ui,
                coordinate_input_dialog_ui,
                new_section_dialog_ui,
                new_material_dialog_ui,
                restraint_assignment_dialog_ui,
                element_table_ui,
                labels_overlay_ui,
                apply_ui_theme,
            ),
        )
        .run();
}

/// Initializes camera and lighting for an empty workspace.
fn setup_scene(mut commands: Commands<'_, '_>) {
    spawn_camera_and_light(&mut commands);
}

fn spawn_camera_and_light(commands: &mut Commands<'_, '_>) {
    let mut pan_orbit = PanOrbitCamera::default();
    pan_orbit.button_orbit = MouseButton::Right;
    pan_orbit.button_pan = MouseButton::Middle;
    pan_orbit.focus = DEFAULT_CENTER;
    pan_orbit.target_focus = DEFAULT_CENTER;
    pan_orbit.radius = Some(DEFAULT_EYE.distance(DEFAULT_CENTER));
    pan_orbit.target_radius = DEFAULT_EYE.distance(DEFAULT_CENTER);

    commands.spawn((
        Camera3d::default(),
        MeshPickingCamera,
        Transform::from_translation(DEFAULT_EYE).looking_at(DEFAULT_CENTER, Vec3::Z),
        MainCamera,
        pan_orbit,
        Name::new("Main Camera"),
    ));

    commands.spawn((
        DirectionalLight {
            shadows_enabled: false,
            illuminance: 20_000.0,
            ..default()
        },
        Transform::from_xyz(50.0, -30.0, 120.0).looking_at(DEFAULT_CENTER, Vec3::Z),
        Name::new("Sun Light"),
    ));
}

fn spawn_node_entities(
    commands: &mut Commands<'_, '_>,
    meshes: &mut Assets<Mesh>,
    node_materials: &mut Assets<StandardMaterial>,
    project: &Project,
    node_size: f32,
) -> std::collections::HashMap<u32, Vec3> {
    let mut node_positions = std::collections::HashMap::with_capacity(project.nodes.len());
    let mesh = meshes.add(Sphere::new(1.0).mesh().uv(12, 8));
    let material = node_materials.add(StandardMaterial {
        base_color: Color::srgb(0.92, 0.92, 0.95),
        unlit: true,
        ..default()
    });

    for node in project.nodes.values() {
        let position = Vec3::new(node.x as f32, node.y as f32, node.z as f32);
        node_positions.insert(node.id, position);
        commands.spawn((
            Mesh3d(mesh.clone()),
            MeshMaterial3d(material.clone()),
            Pickable::IGNORE,
            StructuralNode {
                id: node.id,
                position: node.coords(),
                floor: node.floor,
                zone: NodeZone::from_str(&node.zone),
                restraints: node.restraints,
            },
            NodeMarker,
            Transform::from_translation(position).with_scale(Vec3::splat(node_size.max(0.02))),
            Name::new(format!("Node {}", node.id)),
        ));
    }

    node_positions
}

fn spawn_element_entities(
    commands: &mut Commands<'_, '_>,
    meshes: &mut Assets<Mesh>,
    materials: &mut Assets<SectionCutMaterial>,
    project: &Project,
    node_positions: &std::collections::HashMap<u32, Vec3>,
) {
    for element in project.elements.values() {
        let Some(a) = node_positions.get(&element.node_i).copied() else {
            continue;
        };
        let Some(b) = node_positions.get(&element.node_j).copied() else {
            continue;
        };

        let direction = b - a;
        let length = direction.length();
        if length <= f32::EPSILON {
            continue;
        }

        let midpoint = (a + b) * 0.5;
        let rotation = Quat::from_rotation_arc(Vec3::X, direction.normalize());
        let (size_y, size_z) = section_render_dims(project, element);
        let pick_mesh = meshes.add(Cuboid::new(length, size_y, size_z));
        let pick_material = materials.add(SectionCutMaterial {
            params: dask_modeler::ecs::systems::section_cut::SectionCutUniforms {
                base_color: Vec4::new(1.0, 1.0, 1.0, 0.35),
                plane_xy: Vec4::new(0.0, 0.0, 1.0, 0.0),
                plane_xz: Vec4::new(0.0, 1.0, 0.0, 0.0),
                plane_yz: Vec4::new(1.0, 0.0, 0.0, 0.0),
                flags: Vec4::new(0.0, 0.0, 0.0, 1.0),
            },
            alpha_mode: AlphaMode::Blend,
        });

        commands.spawn((
            Mesh3d(pick_mesh),
            MeshMaterial3d(pick_material),
            Transform::from_translation(midpoint).with_rotation(rotation),
            Pickable::default(),
            StructuralElement {
                id: element.id,
                node_i: element.node_i,
                node_j: element.node_j,
                element_type: element.element_type.clone().into(),
                section_id: element.section_id,
                material_id: element.material_id,
                releases_i: element.releases_i,
                releases_j: element.releases_j,
            },
            ElementMarker,
            Name::new(format!("Element {}", element.id)),
        ));
    }
}

fn section_render_dims(
    project: &Project,
    element: &dask_modeler::model::ElementData,
) -> (f32, f32) {
    let Some(section_id) = element.section_id else {
        return (0.08, 0.08);
    };
    let Some(section) = project.sections.get(&section_id) else {
        return (0.08, 0.08);
    };

    match &section.shape {
        dask_modeler::model::SectionShape::Rectangular { width, height } => {
            ((*width).max(0.08) as f32, (*height).max(0.08) as f32)
        }
        dask_modeler::model::SectionShape::IBeam {
            flange_w,
            flange_t: _,
            web_h,
            web_t: _,
        } => (
            (*flange_w).max(0.08) as f32,
            (*web_h + 2.0).max(0.08) as f32,
        ),
        dask_modeler::model::SectionShape::Circular { diameter } => {
            ((*diameter).max(0.08) as f32, (*diameter).max(0.08) as f32)
        }
        dask_modeler::model::SectionShape::Pipe {
            outer_d,
            inner_d: _,
        } => ((*outer_d).max(0.08) as f32, (*outer_d).max(0.08) as f32),
        dask_modeler::model::SectionShape::LAngle {
            leg_a,
            leg_b,
            thickness: _,
        } => ((*leg_a).max(0.08) as f32, (*leg_b).max(0.08) as f32),
    }
}

/// Scans `data/` for position/connectivity dataset pairs and populates model catalog.
fn initialize_model_catalog(mut catalog: ResMut<'_, ModelCatalog>) {
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("data");
    catalog.datasets = discover_datasets(&data_dir);
    if let Some(base_index) = catalog.datasets.iter().position(|d| d.label == "Base") {
        catalog.selected_index = base_index;
    } else {
        catalog.selected_index = 0;
    }
    catalog.load_requested = false;
}

/// Loads user-selected dataset from toolbar model opener.
fn load_selected_model_from_catalog(
    mut catalog: ResMut<'_, ModelCatalog>,
    mut file_dialog: ResMut<'_, FileDialogState>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut model_change: ResMut<'_, ModelChangeState>,
    mut selection: ResMut<'_, SelectionState>,
    mut drawing_state: ResMut<'_, DrawingState>,
) {
    if !catalog.load_requested {
        return;
    }
    catalog.load_requested = false;

    let Some(dataset) = catalog.datasets.get(catalog.selected_index) else {
        return;
    };

    match Project::from_csv(&dataset.position_csv, &dataset.connectivity_csv) {
        Ok(project) => {
            info!(
                "Loaded dataset {} with {} nodes and {} elements",
                dataset.label,
                project.nodes.len(),
                project.elements.len()
            );
            apply_loaded_project(
                project,
                &mut project_res,
                &mut undo_stack,
                &mut selection,
                &mut drawing_state,
                &mut model_change,
            );
            file_dialog.active_json_path = None;
        }
        Err(err) => {
            error!(
                "Failed to load dataset {}: {} / {} ({err:#})",
                dataset.label,
                dataset.position_csv.display(),
                dataset.connectivity_csv.display()
            );
        }
    }
}

/// Loads model files selected through the native File/Open dialog.
fn load_model_from_file_dialog(
    mut file_dialog: ResMut<'_, FileDialogState>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut model_change: ResMut<'_, ModelChangeState>,
    mut selection: ResMut<'_, SelectionState>,
    mut drawing_state: ResMut<'_, DrawingState>,
) {
    let Some(request) = file_dialog.pending_open.take() else {
        return;
    };

    let result = match &request {
        FileOpenRequest::CsvPair {
            position_csv,
            connectivity_csv,
        } => Project::from_csv(position_csv, connectivity_csv),
        FileOpenRequest::JsonProject { path } => load_project_json(path),
    };

    match result {
        Ok(project) => {
            info!(
                "Loaded model with {} nodes and {} elements from File/Open",
                project.nodes.len(),
                project.elements.len()
            );
            apply_loaded_project(
                project,
                &mut project_res,
                &mut undo_stack,
                &mut selection,
                &mut drawing_state,
                &mut model_change,
            );
            match request {
                FileOpenRequest::CsvPair {
                    position_csv,
                    connectivity_csv: _,
                } => {
                    file_dialog.active_json_path = None;
                    file_dialog.last_directory = position_csv.parent().map(PathBuf::from);
                }
                FileOpenRequest::JsonProject { path } => {
                    file_dialog.active_json_path = Some(path.clone());
                    file_dialog.last_directory = path.parent().map(PathBuf::from);
                }
            }
        }
        Err(err) => match request {
            FileOpenRequest::CsvPair {
                position_csv,
                connectivity_csv,
            } => error!(
                "Failed to load csv pair {} / {} ({err:#})",
                position_csv.display(),
                connectivity_csv.display()
            ),
            FileOpenRequest::JsonProject { path } => {
                error!("Failed to load json project {} ({err:#})", path.display())
            }
        },
    }
}

/// Handles file menu save/new requests.
fn handle_file_menu_actions(
    mut file_dialog: ResMut<'_, FileDialogState>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut model_change: ResMut<'_, ModelChangeState>,
    mut selection: ResMut<'_, SelectionState>,
    mut drawing_state: ResMut<'_, DrawingState>,
) {
    if file_dialog.new_model_requested {
        file_dialog.new_model_requested = false;
        apply_loaded_project(
            Project::new("Untitled Model"),
            &mut project_res,
            &mut undo_stack,
            &mut selection,
            &mut drawing_state,
            &mut model_change,
        );
        file_dialog.active_json_path = None;
        info!("Started new empty model");
    }

    let Some(path) = file_dialog.pending_save.take() else {
        if let Some(export_request) = file_dialog.pending_export.take() {
            match export_request {
                ExportRequest::ConnectivityCsv { path } => {
                    if let Err(err) = export_connectivity_csv(&project_res.project, &path) {
                        error!(
                            "Failed to export connectivity csv {} ({err:#})",
                            path.display()
                        );
                    } else {
                        info!("Exported connectivity csv to {}", path.display());
                    }
                }
                ExportRequest::AdjacencyDenseCsv { path } => {
                    if let Err(err) = export_adjacency_dense_csv(&project_res.project, &path) {
                        error!(
                            "Failed to export dense adjacency csv {} ({err:#})",
                            path.display()
                        );
                    } else {
                        info!("Exported dense adjacency csv to {}", path.display());
                    }
                }
                ExportRequest::AdjacencySparseCsrCsv { path } => {
                    if let Err(err) = export_adjacency_sparse_csr_csv(&project_res.project, &path) {
                        error!(
                            "Failed to export sparse adjacency csv {} ({err:#})",
                            path.display()
                        );
                    } else {
                        info!("Exported sparse adjacency csv to {}", path.display());
                    }
                }
                ExportRequest::OpenSeesTcl { path } => {
                    if let Err(err) = export_opensees_tcl(&project_res.project, &path) {
                        error!("Failed to export OpenSees TCL {} ({err:#})", path.display());
                    } else {
                        info!("Exported OpenSees TCL to {}", path.display());
                    }
                }
            }
        }
        return;
    };

    match save_project_json(&project_res.project, &path) {
        Ok(()) => {
            file_dialog.active_json_path = Some(path.clone());
            file_dialog.last_directory = path.parent().map(PathBuf::from);
            push_recent_json(&mut file_dialog, path);
            info!("Saved project json");
        }
        Err(err) => error!("Failed to save project json ({err:#})"),
    }
}

fn handle_model_edit_requests(
    mut restraint_dialog: ResMut<'_, RestraintDialogState>,
    mut node_merge: ResMut<'_, NodeMergeState>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut model_change: ResMut<'_, ModelChangeState>,
    mut selection: ResMut<'_, SelectionState>,
) {
    if restraint_dialog.apply_requested {
        restraint_dialog.apply_requested = false;
        let node_ids = selected_node_ids(&selection, &project_res.project);
        if !node_ids.is_empty() {
            let restraints = [
                restraint_dialog.ux,
                restraint_dialog.uy,
                restraint_dialog.uz,
                restraint_dialog.rx,
                restraint_dialog.ry,
                restraint_dialog.rz,
            ];
            let command = AssignRestraintsCommand::new(node_ids, restraints);
            match undo_stack.execute(Box::new(command), &mut project_res.project) {
                Ok(()) => model_change.dirty = true,
                Err(err) => error!("Failed to assign restraints ({err:#})"),
            }
        }
    }

    if node_merge.merge_requested {
        node_merge.merge_requested = false;
        let candidates = selected_node_ids(&selection, &project_res.project);
        let command = if candidates.is_empty() {
            MergeNodesCommand::new(node_merge.tolerance.max(1e-9))
        } else {
            MergeNodesCommand::new_for_nodes(node_merge.tolerance.max(1e-9), candidates)
        };
        match undo_stack.execute(Box::new(command), &mut project_res.project) {
            Ok(()) => {
                selection.selected_elements.clear();
                selection.selected_nodes.clear();
                model_change.dirty = true;
            }
            Err(err) => error!("Failed to merge nodes ({err:#})"),
        }
    }
}

fn selected_node_ids(selection: &SelectionState, project: &Project) -> Vec<u32> {
    let mut ids = selection.selected_nodes.clone();
    if ids.is_empty() {
        for element_id in &selection.selected_elements {
            if let Some(element) = project.elements.get(element_id) {
                ids.push(element.node_i);
                ids.push(element.node_j);
            }
        }
    }
    ids.sort_unstable();
    ids.dedup();
    ids
}

fn push_recent_json(file_dialog: &mut FileDialogState, path: PathBuf) {
    let label = format!(
        "JSON: {}",
        path.file_name()
            .and_then(|s| s.to_str())
            .unwrap_or("project.json")
    );
    file_dialog.recent.retain(|entry| entry.label != label);
    file_dialog.recent.insert(
        0,
        dask_modeler::ecs::resources::RecentModelEntry {
            label,
            request: FileOpenRequest::JsonProject { path },
        },
    );
    if file_dialog.recent.len() > 8 {
        file_dialog.recent.truncate(8);
    }
}

fn apply_loaded_project(
    project: Project,
    project_res: &mut ProjectResource,
    undo_stack: &mut UndoStack,
    selection: &mut SelectionState,
    drawing_state: &mut DrawingState,
    model_change: &mut ModelChangeState,
) {
    project_res.project = project;
    undo_stack.clear();
    selection.selected_elements.clear();
    selection.selected_nodes.clear();
    drawing_state.first_node = None;
    drawing_state.preview_end = None;
    model_change.dirty = true;
}

/// Rebuilds ECS node/element entities from project when model changes.
fn rebuild_model_entities_if_dirty(
    mut commands: Commands<'_, '_>,
    mut meshes: ResMut<'_, Assets<Mesh>>,
    mut node_materials: ResMut<'_, Assets<StandardMaterial>>,
    mut materials: ResMut<'_, Assets<SectionCutMaterial>>,
    mut model_change: ResMut<'_, ModelChangeState>,
    mut stats: ResMut<'_, ModelStats>,
    mut selection: ResMut<'_, SelectionState>,
    display: Res<'_, DisplaySettings>,
    project_res: Res<'_, ProjectResource>,
    nodes: Query<'_, '_, Entity, With<NodeMarker>>,
    elements: Query<'_, '_, Entity, With<ElementMarker>>,
) {
    if !model_change.dirty {
        return;
    }

    for entity in &nodes {
        commands.entity(entity).despawn();
    }
    for entity in &elements {
        commands.entity(entity).despawn();
    }

    let node_positions = spawn_node_entities(
        &mut commands,
        &mut meshes,
        &mut node_materials,
        &project_res.project,
        display.node_size,
    );
    spawn_element_entities(
        &mut commands,
        &mut meshes,
        &mut materials,
        &project_res.project,
        &node_positions,
    );

    stats.total_nodes = project_res.project.nodes.len();
    stats.total_elements = project_res.project.elements.len();
    stats.total_dofs = stats.total_nodes * 6;
    stats.selected_count = 0;
    selection.selected_elements.clear();
    selection.selected_nodes.clear();
    model_change.dirty = false;
}

fn discover_datasets(data_dir: &PathBuf) -> Vec<ModelDataset> {
    let mut datasets = Vec::new();
    let Ok(entries) = fs::read_dir(data_dir) else {
        return datasets;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        let Some(name) = path.file_name().and_then(|n| n.to_str()) else {
            continue;
        };
        if !name.ends_with(".csv") || !name.contains("position_matrix") {
            continue;
        }

        let connectivity_name = name.replace("position_matrix", "connectivity_matrix");
        let connectivity_path = data_dir.join(&connectivity_name);
        if !connectivity_path.exists() {
            continue;
        }

        datasets.push(ModelDataset {
            label: dataset_label_from_filename(name),
            position_csv: path.clone(),
            connectivity_csv: connectivity_path,
        });
    }

    datasets.sort_by(|a, b| a.label.cmp(&b.label));
    datasets
}

fn dataset_label_from_filename(name: &str) -> String {
    if name == "position_matrix.csv" {
        return "Base".to_string();
    }
    if let Some(raw) = name
        .strip_prefix("twin_position_matrix_")
        .and_then(|s| s.strip_suffix(".csv"))
    {
        return raw.trim_start_matches('_').to_uppercase();
    }
    name.strip_suffix(".csv").unwrap_or(name).to_string()
}
