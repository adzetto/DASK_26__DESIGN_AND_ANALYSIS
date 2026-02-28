//! Element table UI panel.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::resources::{ElementTableSortBy, ElementTableState, ProjectResource, UiSettings};

#[derive(Clone)]
struct ElementRow {
    id: u32,
    node_i: u32,
    node_j: u32,
    kind: String,
    length: f64,
    section: String,
    material: String,
}

/// Draws sortable/filterable element data table.
pub fn element_table_ui(
    mut contexts: EguiContexts<'_, '_>,
    mut state: ResMut<'_, ElementTableState>,
    project: Res<'_, ProjectResource>,
    ui_settings: Res<'_, UiSettings>,
) {
    if !state.show {
        return;
    }
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    egui::TopBottomPanel::bottom("element_table_panel")
        .resizable(true)
        .default_height(220.0)
        .show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.heading(if ui_settings.turkish {
                    "Eleman Tablosu"
                } else {
                    "Element Table"
                });
                ui.separator();
                ui.label(if ui_settings.turkish {
                    "Filtre"
                } else {
                    "Filter"
                });
                ui.text_edit_singleline(&mut state.filter_text);
                ui.separator();
                ui.label(if ui_settings.turkish {
                    "Siralama"
                } else {
                    "Sort"
                });
                egui::ComboBox::from_id_salt("element_table_sort")
                    .selected_text(sort_label(state.sort_by, ui_settings.turkish))
                    .show_ui(ui, |ui| {
                        ui.selectable_value(
                            &mut state.sort_by,
                            ElementTableSortBy::Id,
                            sort_label(ElementTableSortBy::Id, ui_settings.turkish),
                        );
                        ui.selectable_value(
                            &mut state.sort_by,
                            ElementTableSortBy::Type,
                            sort_label(ElementTableSortBy::Type, ui_settings.turkish),
                        );
                        ui.selectable_value(
                            &mut state.sort_by,
                            ElementTableSortBy::Length,
                            sort_label(ElementTableSortBy::Length, ui_settings.turkish),
                        );
                        ui.selectable_value(
                            &mut state.sort_by,
                            ElementTableSortBy::NodeI,
                            sort_label(ElementTableSortBy::NodeI, ui_settings.turkish),
                        );
                        ui.selectable_value(
                            &mut state.sort_by,
                            ElementTableSortBy::NodeJ,
                            sort_label(ElementTableSortBy::NodeJ, ui_settings.turkish),
                        );
                    });
                ui.checkbox(
                    &mut state.ascending,
                    if ui_settings.turkish {
                        "Artan"
                    } else {
                        "Ascending"
                    },
                );
            });

            let mut rows = element_rows(&project.project);
            apply_filter(&mut rows, &state.filter_text);
            apply_sort(&mut rows, state.sort_by, state.ascending);

            egui::ScrollArea::vertical().show(ui, |ui| {
                egui::Grid::new("element_table_grid")
                    .striped(true)
                    .min_col_width(70.0)
                    .show(ui, |ui| {
                        ui.label("ID");
                        ui.label("Tip");
                        ui.label("i");
                        ui.label("j");
                        ui.label("L");
                        ui.label("Kesit");
                        ui.label("Malzeme");
                        ui.end_row();

                        for row in rows {
                            ui.label(row.id.to_string());
                            ui.label(row.kind);
                            ui.label(row.node_i.to_string());
                            ui.label(row.node_j.to_string());
                            ui.label(format!("{:.3}", row.length));
                            ui.label(row.section);
                            ui.label(row.material);
                            ui.end_row();
                        }
                    });
            });
        });
}

fn sort_label(sort_by: ElementTableSortBy, turkish: bool) -> &'static str {
    if turkish {
        match sort_by {
            ElementTableSortBy::Id => "Kimlik",
            ElementTableSortBy::Type => "Tip",
            ElementTableSortBy::Length => "Boy",
            ElementTableSortBy::NodeI => "Dugum i",
            ElementTableSortBy::NodeJ => "Dugum j",
        }
    } else {
        match sort_by {
            ElementTableSortBy::Id => "ID",
            ElementTableSortBy::Type => "Type",
            ElementTableSortBy::Length => "Length",
            ElementTableSortBy::NodeI => "Node i",
            ElementTableSortBy::NodeJ => "Node j",
        }
    }
}

fn element_rows(project: &crate::model::Project) -> Vec<ElementRow> {
    let mut out = Vec::with_capacity(project.elements.len());
    for element in project.elements.values() {
        out.push(ElementRow {
            id: element.id,
            node_i: element.node_i,
            node_j: element.node_j,
            kind: element.element_type.as_str().to_string(),
            length: element.length,
            section: element
                .section_id
                .and_then(|id| project.sections.get(&id))
                .map(|s| s.name.clone())
                .unwrap_or_else(|| "-".to_string()),
            material: element
                .material_id
                .and_then(|id| project.materials.get(&id))
                .map(|m| m.name.clone())
                .unwrap_or_else(|| "-".to_string()),
        });
    }
    out
}

fn apply_filter(rows: &mut Vec<ElementRow>, needle: &str) {
    let needle = needle.trim();
    if needle.is_empty() {
        return;
    }
    let lower = needle.to_lowercase();
    rows.retain(|r| {
        r.id.to_string().contains(&lower)
            || r.node_i.to_string().contains(&lower)
            || r.node_j.to_string().contains(&lower)
            || r.kind.to_lowercase().contains(&lower)
            || r.section.to_lowercase().contains(&lower)
            || r.material.to_lowercase().contains(&lower)
    });
}

fn apply_sort(rows: &mut [ElementRow], sort_by: ElementTableSortBy, ascending: bool) {
    rows.sort_by(|a, b| {
        let ord = match sort_by {
            ElementTableSortBy::Id => a.id.cmp(&b.id),
            ElementTableSortBy::Type => a.kind.cmp(&b.kind),
            ElementTableSortBy::Length => a
                .length
                .partial_cmp(&b.length)
                .unwrap_or(std::cmp::Ordering::Equal),
            ElementTableSortBy::NodeI => a.node_i.cmp(&b.node_i),
            ElementTableSortBy::NodeJ => a.node_j.cmp(&b.node_j),
        };
        if ascending { ord } else { ord.reverse() }
    });
}
