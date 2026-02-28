//! Top toolbar panel.

use std::path::PathBuf;

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};
use rfd::FileDialog;

use crate::commands::MirrorPlane;
use crate::ecs::resources::{
    ColorMode, CoordinateInputState, DisplaySettings, DrawingState, ElementTableState,
    ExportRequest, FileDialogState, FileOpenRequest, ModelCatalog, NewMaterialDialogState,
    NewSectionDialogState, RecentModelEntry, SelectionTypeFilter, ToolMode, TransformOpsState,
    UiSettings, ViewMode,
};

/// Draws the top toolbar for view/tool/display controls.
pub fn toolbar_ui(
    mut contexts: EguiContexts<'_, '_>,
    mut display: ResMut<'_, DisplaySettings>,
    mut tool_mode: ResMut<'_, ToolMode>,
    mut view_mode: ResMut<'_, ViewMode>,
    mut model_catalog: ResMut<'_, ModelCatalog>,
    mut coordinate_input: ResMut<'_, CoordinateInputState>,
    mut drawing_state: ResMut<'_, DrawingState>,
    mut type_filter: ResMut<'_, SelectionTypeFilter>,
    mut transform_ops: ResMut<'_, TransformOpsState>,
    mut file_dialog: ResMut<'_, FileDialogState>,
    mut section_dialog: ResMut<'_, NewSectionDialogState>,
    mut material_dialog: ResMut<'_, NewMaterialDialogState>,
    mut ui_settings: ResMut<'_, UiSettings>,
    mut element_table: ResMut<'_, ElementTableState>,
) {
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    egui::TopBottomPanel::top("toolbar_panel").show(ctx, |ui| {
        ui.horizontal_wrapped(|ui| {
            draw_file_menu(
                ui,
                &mut file_dialog,
                &mut section_dialog,
                &mut material_dialog,
            );
            ui.separator();
            draw_model_opener(ui, &mut model_catalog);
            ui.separator();
            draw_view_buttons(ui, &mut view_mode);
            ui.separator();
            draw_tool_buttons(ui, &mut tool_mode);

            if matches!(
                *tool_mode,
                ToolMode::DrawBeam | ToolMode::DrawColumn | ToolMode::DrawBrace
            ) {
                ui.checkbox(&mut drawing_state.continuous, "Surekli (Tab)");
                if ui.button("Koordinat").clicked() {
                    coordinate_input.open = true;
                }
            }

            ui.separator();
            draw_transform_buttons(ui, &mut transform_ops);
            ui.separator();
            draw_display_controls(ui, &mut display);
            ui.separator();
            ui.menu_button("Secim Filtresi", |ui| {
                draw_selection_type_filter(ui, &mut type_filter);
            });
            ui.separator();
            draw_ui_controls(ui, &mut ui_settings, &mut element_table);
        });
    });

    draw_move_window(ctx, &mut transform_ops);
    draw_copy_window(ctx, &mut transform_ops);
    draw_array_window(ctx, &mut transform_ops);
    draw_mirror_window(ctx, &mut transform_ops);
}

fn draw_model_opener(ui: &mut egui::Ui, model_catalog: &mut ModelCatalog) {
    ui.label("Model:");
    if model_catalog.datasets.is_empty() {
        ui.label("Veri seti yok");
        return;
    }

    let current_label = model_catalog
        .datasets
        .get(model_catalog.selected_index)
        .map(|d| d.label.as_str())
        .unwrap_or("Sec");

    egui::ComboBox::from_label("")
        .selected_text(current_label)
        .show_ui(ui, |ui| {
            let labels: Vec<String> = model_catalog
                .datasets
                .iter()
                .map(|d| d.label.clone())
                .collect();
            for (idx, label) in labels.iter().enumerate() {
                ui.selectable_value(&mut model_catalog.selected_index, idx, label);
            }
        });

    if ui.button("Model Ac").clicked() {
        model_catalog.load_requested = true;
    }
}

fn draw_file_menu(
    ui: &mut egui::Ui,
    file_dialog: &mut FileDialogState,
    section_dialog: &mut NewSectionDialogState,
    material_dialog: &mut NewMaterialDialogState,
) {
    ui.menu_button("Dosya", |ui| {
        if ui.button("Yeni Model").clicked() {
            file_dialog.new_model_requested = true;
            ui.close();
        }

        ui.separator();
        if ui.button("CSV Cifti Ac...").clicked() {
            request_open_csv_pair(file_dialog);
            ui.close();
        }
        if ui.button("JSON Proje Ac...").clicked() {
            request_open_json(file_dialog);
            ui.close();
        }

        ui.separator();
        if ui.button("JSON Kaydet").clicked() {
            request_save_json(file_dialog);
            ui.close();
        }
        if ui.button("JSON Farkli Kaydet...").clicked() {
            request_save_json_as(file_dialog);
            ui.close();
        }

        ui.separator();
        if ui.button("Baglanti CSV Disa Aktar...").clicked() {
            request_export_connectivity(file_dialog);
            ui.close();
        }
        if ui.button("Komsuluk Yogun CSV Disa Aktar...").clicked() {
            request_export_adj_dense(file_dialog);
            ui.close();
        }
        if ui.button("Komsuluk Seyrek CSR CSV Disa Aktar...").clicked() {
            request_export_adj_sparse(file_dialog);
            ui.close();
        }
        if ui.button("OpenSees TCL Disa Aktar...").clicked() {
            request_export_opensees(file_dialog);
            ui.close();
        }

        ui.separator();
        if ui.button("Yeni Kesit...").clicked() {
            section_dialog.open = true;
            ui.close();
        }
        if ui.button("Yeni Malzeme...").clicked() {
            material_dialog.open = true;
            ui.close();
        }

        if !file_dialog.recent.is_empty() {
            ui.separator();
            ui.label("Son Dosyalar");
            let entries = file_dialog.recent.clone();
            for entry in entries {
                if ui.button(entry.label).clicked() {
                    file_dialog.pending_open = Some(entry.request);
                    ui.close();
                }
            }
        }
    });
}

fn draw_view_buttons(ui: &mut egui::Ui, view_mode: &mut ViewMode) {
    ui.label("Gorunum:");
    if ui
        .selectable_label(*view_mode == ViewMode::View3D, "3B")
        .clicked()
    {
        *view_mode = ViewMode::View3D;
    }
    if ui
        .selectable_label(*view_mode == ViewMode::Plan, "Plan")
        .clicked()
    {
        *view_mode = ViewMode::Plan;
    }
    if ui
        .selectable_label(*view_mode == ViewMode::Front, "On")
        .clicked()
    {
        *view_mode = ViewMode::Front;
    }
    if ui
        .selectable_label(*view_mode == ViewMode::Side, "Yan")
        .clicked()
    {
        *view_mode = ViewMode::Side;
    }
}

fn draw_tool_buttons(ui: &mut egui::Ui, tool_mode: &mut ToolMode) {
    ui.label("Arac:");
    if ui
        .selectable_label(*tool_mode == ToolMode::Select, "Sec")
        .clicked()
    {
        *tool_mode = ToolMode::Select;
    }
    if ui
        .selectable_label(*tool_mode == ToolMode::DrawBeam, "Kiris Ciz")
        .clicked()
    {
        *tool_mode = ToolMode::DrawBeam;
    }
    if ui
        .selectable_label(*tool_mode == ToolMode::DrawColumn, "Kolon Ciz")
        .clicked()
    {
        *tool_mode = ToolMode::DrawColumn;
    }
    if ui
        .selectable_label(*tool_mode == ToolMode::DrawBrace, "Capraz Ciz")
        .clicked()
    {
        *tool_mode = ToolMode::DrawBrace;
    }
    if ui
        .selectable_label(*tool_mode == ToolMode::MoveNode, "Tasi")
        .clicked()
    {
        *tool_mode = ToolMode::MoveNode;
    }
}

fn draw_transform_buttons(ui: &mut egui::Ui, ops: &mut TransformOpsState) {
    ui.label("Donusum:");
    if ui.button("Tasi (M)").clicked() {
        ops.move_open = true;
    }
    if ui.button("Kopyala (Ctrl+D)").clicked() {
        ops.copy_open = true;
    }
    if ui.button("Dizi").clicked() {
        ops.array_open = true;
    }
    if ui.button("Aynala").clicked() {
        ops.mirror_open = true;
    }
}

fn draw_display_controls(ui: &mut egui::Ui, display: &mut DisplaySettings) {
    ui.checkbox(&mut display.show_nodes, "Dugumler");
    ui.checkbox(&mut display.show_labels, "Etiketler");
    ui.checkbox(&mut display.show_grid, "Izgara");
    ui.checkbox(&mut display.show_restraints, "Mesnet Simge");
    ui.add(egui::Slider::new(&mut display.lod_distance, 100.0..=3000.0).text("LOD"));

    egui::ComboBox::from_label("Renk")
        .selected_text(match display.color_mode {
            ColorMode::ByElementType => "Tipe Gore",
            ColorMode::BySection => "Kesite Gore",
            ColorMode::ByMaterial => "Malzemeye Gore",
            ColorMode::ByFloor => "Kata Gore",
            ColorMode::Uniform => "Tek Renk",
        })
        .show_ui(ui, |ui| {
            ui.selectable_value(
                &mut display.color_mode,
                ColorMode::ByElementType,
                "Tipe Gore",
            );
            ui.selectable_value(&mut display.color_mode, ColorMode::BySection, "Kesite Gore");
            ui.selectable_value(
                &mut display.color_mode,
                ColorMode::ByMaterial,
                "Malzemeye Gore",
            );
            ui.selectable_value(&mut display.color_mode, ColorMode::ByFloor, "Kata Gore");
            ui.selectable_value(&mut display.color_mode, ColorMode::Uniform, "Tek Renk");
        });
}

fn draw_selection_type_filter(ui: &mut egui::Ui, filter: &mut SelectionTypeFilter) {
    ui.label("Secilebilir tipler");
    ui.checkbox(&mut filter.beam_x, "beam_x");
    ui.checkbox(&mut filter.beam_y, "beam_y");
    ui.checkbox(&mut filter.column, "column");
    ui.checkbox(&mut filter.brace_xz, "brace_xz");
    ui.checkbox(&mut filter.brace_yz, "brace_yz");
    ui.checkbox(&mut filter.brace_floor, "brace_floor");
    ui.checkbox(&mut filter.core_wall, "core_wall");
    ui.checkbox(&mut filter.chevron, "chevron");
    ui.checkbox(&mut filter.brace_space, "brace_space");
    ui.checkbox(&mut filter.custom, "custom");
}

fn draw_ui_controls(ui: &mut egui::Ui, settings: &mut UiSettings, table: &mut ElementTableState) {
    ui.menu_button("Arayuz", |ui| {
        ui.checkbox(&mut settings.dark_theme, "Koyu Tema");
        ui.checkbox(&mut settings.turkish, "Turkce");
        ui.checkbox(&mut table.show, "Eleman Tablosu");
    });
}

fn draw_move_window(ctx: &egui::Context, ops: &mut TransformOpsState) {
    if !ops.move_open {
        return;
    }
    egui::Window::new("Dugum Tasi")
        .open(&mut ops.move_open)
        .show(ctx, |ui| {
            ui.label("Secili dugum/elemanlari ofset ile tasi");
            ui.horizontal(|ui| {
                ui.label("dX");
                ui.add(egui::DragValue::new(&mut ops.move_dx).speed(0.1));
                ui.label("dY");
                ui.add(egui::DragValue::new(&mut ops.move_dy).speed(0.1));
                ui.label("dZ");
                ui.add(egui::DragValue::new(&mut ops.move_dz).speed(0.1));
            });
            if ui.button("Uygula").clicked() {
                ops.move_apply_requested = true;
            }
        });
}

fn draw_copy_window(ctx: &egui::Context, ops: &mut TransformOpsState) {
    if !ops.copy_open {
        return;
    }
    egui::Window::new("Eleman Kopyala")
        .open(&mut ops.copy_open)
        .show(ctx, |ui| {
            ui.label("Secili elemanlari ofset ile kopyala");
            ui.horizontal(|ui| {
                ui.label("dX");
                ui.add(egui::DragValue::new(&mut ops.copy_dx).speed(0.1));
                ui.label("dY");
                ui.add(egui::DragValue::new(&mut ops.copy_dy).speed(0.1));
                ui.label("dZ");
                ui.add(egui::DragValue::new(&mut ops.copy_dz).speed(0.1));
            });
            if ui.button("Uygula").clicked() {
                ops.copy_apply_requested = true;
            }
        });
}

fn draw_array_window(ctx: &egui::Context, ops: &mut TransformOpsState) {
    if !ops.array_open {
        return;
    }
    egui::Window::new("Dogrusal Dizi")
        .open(&mut ops.array_open)
        .show(ctx, |ui| {
            ui.label("Esit araliklarla N kopya uret");
            ui.horizontal(|ui| {
                ui.label("dX");
                ui.add(egui::DragValue::new(&mut ops.array_dx).speed(0.1));
                ui.label("dY");
                ui.add(egui::DragValue::new(&mut ops.array_dy).speed(0.1));
                ui.label("dZ");
                ui.add(egui::DragValue::new(&mut ops.array_dz).speed(0.1));
            });
            ui.horizontal(|ui| {
                ui.label("Adet");
                ui.add(egui::DragValue::new(&mut ops.array_count).range(1..=200));
            });
            if ui.button("Uygula").clicked() {
                ops.array_apply_requested = true;
            }
        });
}

fn draw_mirror_window(ctx: &egui::Context, ops: &mut TransformOpsState) {
    if !ops.mirror_open {
        return;
    }
    egui::Window::new("Eleman Aynala")
        .open(&mut ops.mirror_open)
        .show(ctx, |ui| {
            ui.label("Secili elemanlari aynala ve kopyasini olustur");
            ui.horizontal(|ui| {
                ui.selectable_value(&mut ops.mirror_plane, MirrorPlane::XY, "XY");
                ui.selectable_value(&mut ops.mirror_plane, MirrorPlane::XZ, "XZ");
                ui.selectable_value(&mut ops.mirror_plane, MirrorPlane::YZ, "YZ");
            });
            ui.horizontal(|ui| {
                ui.label("Duzlem konumu");
                ui.add(egui::DragValue::new(&mut ops.mirror_position).speed(0.1));
            });
            if ui.button("Uygula").clicked() {
                ops.mirror_apply_requested = true;
            }
        });
}

fn request_open_csv_pair(file_dialog: &mut FileDialogState) {
    let Some(position_csv) = pick_file(
        "Konum Matrisi CSV Sec",
        &["csv"],
        file_dialog.last_directory.as_ref(),
    ) else {
        return;
    };
    file_dialog.last_directory = parent_dir(&position_csv);

    let Some(connectivity_csv) = pick_file(
        "Baglanti Matrisi CSV Sec",
        &["csv"],
        file_dialog.last_directory.as_ref(),
    ) else {
        return;
    };
    file_dialog.last_directory = parent_dir(&connectivity_csv);

    let request = FileOpenRequest::CsvPair {
        position_csv: position_csv.clone(),
        connectivity_csv: connectivity_csv.clone(),
    };
    file_dialog.pending_open = Some(request.clone());
    remember_recent(file_dialog, request);
}

fn request_open_json(file_dialog: &mut FileDialogState) {
    let Some(path) = pick_file(
        "JSON Proje Ac",
        &["json"],
        file_dialog.last_directory.as_ref(),
    ) else {
        return;
    };
    file_dialog.last_directory = parent_dir(&path);
    let request = FileOpenRequest::JsonProject { path: path.clone() };
    file_dialog.pending_open = Some(request.clone());
    remember_recent(file_dialog, request);
}

fn request_save_json(file_dialog: &mut FileDialogState) {
    if let Some(path) = file_dialog.active_json_path.clone() {
        file_dialog.pending_save = Some(path);
        return;
    }
    request_save_json_as(file_dialog);
}

fn request_save_json_as(file_dialog: &mut FileDialogState) {
    let Some(path) = pick_save_file(
        "JSON Proje Kaydet",
        &["json"],
        file_dialog.last_directory.as_ref(),
        "model.json",
    ) else {
        return;
    };
    file_dialog.last_directory = parent_dir(&path);
    file_dialog.active_json_path = Some(path.clone());
    file_dialog.pending_save = Some(path);
}

fn request_export_connectivity(file_dialog: &mut FileDialogState) {
    let Some(path) = pick_save_file(
        "Baglanti CSV Disa Aktar",
        &["csv"],
        file_dialog.last_directory.as_ref(),
        "connectivity_export.csv",
    ) else {
        return;
    };
    file_dialog.last_directory = parent_dir(&path);
    file_dialog.pending_export = Some(ExportRequest::ConnectivityCsv { path });
}

fn request_export_adj_dense(file_dialog: &mut FileDialogState) {
    let Some(path) = pick_save_file(
        "Yogun Komsuluk CSV Disa Aktar",
        &["csv"],
        file_dialog.last_directory.as_ref(),
        "adjacency_dense.csv",
    ) else {
        return;
    };
    file_dialog.last_directory = parent_dir(&path);
    file_dialog.pending_export = Some(ExportRequest::AdjacencyDenseCsv { path });
}

fn request_export_adj_sparse(file_dialog: &mut FileDialogState) {
    let Some(path) = pick_save_file(
        "Seyrek CSR Komsuluk CSV Disa Aktar",
        &["csv"],
        file_dialog.last_directory.as_ref(),
        "adjacency_sparse_csr.csv",
    ) else {
        return;
    };
    file_dialog.last_directory = parent_dir(&path);
    file_dialog.pending_export = Some(ExportRequest::AdjacencySparseCsrCsv { path });
}

fn request_export_opensees(file_dialog: &mut FileDialogState) {
    let Some(path) = pick_save_file(
        "OpenSees TCL Disa Aktar",
        &["tcl", "txt"],
        file_dialog.last_directory.as_ref(),
        "model.tcl",
    ) else {
        return;
    };
    file_dialog.last_directory = parent_dir(&path);
    file_dialog.pending_export = Some(ExportRequest::OpenSeesTcl { path });
}

fn pick_file(title: &str, extensions: &[&str], directory: Option<&PathBuf>) -> Option<PathBuf> {
    let mut dialog = FileDialog::new()
        .set_title(title)
        .add_filter("Desteklenen", extensions);
    if let Some(dir) = directory {
        dialog = dialog.set_directory(dir);
    }
    dialog.pick_file()
}

fn pick_save_file(
    title: &str,
    extensions: &[&str],
    directory: Option<&PathBuf>,
    default_file_name: &str,
) -> Option<PathBuf> {
    let mut dialog = FileDialog::new()
        .set_title(title)
        .set_file_name(default_file_name)
        .add_filter("Desteklenen", extensions);
    if let Some(dir) = directory {
        dialog = dialog.set_directory(dir);
    }
    dialog.save_file()
}

fn parent_dir(path: &PathBuf) -> Option<PathBuf> {
    path.parent().map(PathBuf::from)
}

fn remember_recent(file_dialog: &mut FileDialogState, request: FileOpenRequest) {
    let label = match &request {
        FileOpenRequest::CsvPair {
            position_csv,
            connectivity_csv,
        } => format!(
            "CSV: {} + {}",
            position_csv
                .file_name()
                .and_then(|s| s.to_str())
                .unwrap_or("position.csv"),
            connectivity_csv
                .file_name()
                .and_then(|s| s.to_str())
                .unwrap_or("connectivity.csv")
        ),
        FileOpenRequest::JsonProject { path } => format!(
            "JSON: {}",
            path.file_name()
                .and_then(|s| s.to_str())
                .unwrap_or("project.json")
        ),
    };

    file_dialog.recent.retain(|entry| entry.label != label);
    file_dialog
        .recent
        .insert(0, RecentModelEntry { label, request });
    if file_dialog.recent.len() > 8 {
        file_dialog.recent.truncate(8);
    }
}
