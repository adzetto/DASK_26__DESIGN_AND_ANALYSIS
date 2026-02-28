//! Right-side properties/details panel.

use std::collections::HashMap;

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};
use log::warn;

use crate::commands::{AssignMaterialCommand, AssignSectionCommand, UndoStack};
use crate::ecs::components::{
    ElementMarker, NodeMarker, Selected, StructuralElement, StructuralNode,
};
use crate::ecs::resources::{
    ModelChangeState, ModelStats, NewMaterialDialogState, NewSectionDialogState, NodeMergeState,
    ProjectResource, RestraintDialogState, SelectionState,
};
use crate::model::validation::validate_project;

/// Draws selected element properties or model summary.
pub fn properties_panel_ui(
    mut contexts: EguiContexts<'_, '_>,
    selection: Res<'_, SelectionState>,
    stats: Res<'_, ModelStats>,
    mut project: ResMut<'_, ProjectResource>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut model_change: ResMut<'_, ModelChangeState>,
    mut section_dialog: ResMut<'_, NewSectionDialogState>,
    mut material_dialog: ResMut<'_, NewMaterialDialogState>,
    mut restraint_dialog: ResMut<'_, RestraintDialogState>,
    mut node_merge: ResMut<'_, NodeMergeState>,
    mut section_choice: Local<'_, Option<u32>>,
    mut material_choice: Local<'_, Option<u32>>,
    selected_elements: Query<'_, '_, &StructuralElement, (With<ElementMarker>, With<Selected>)>,
    nodes: Query<'_, '_, &StructuralNode, With<NodeMarker>>,
) {
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    let node_map: HashMap<u32, Vec3> = nodes
        .iter()
        .map(|n| {
            (
                n.id,
                Vec3::new(
                    n.position[0] as f32,
                    n.position[1] as f32,
                    n.position[2] as f32,
                ),
            )
        })
        .collect();

    egui::SidePanel::right("properties_panel")
        .default_width(320.0)
        .show(ctx, |ui| {
            ui.heading("Ozellikler");
            ui.horizontal(|ui| {
                if ui.button("Yeni Kesit").clicked() {
                    section_dialog.open = true;
                }
                if ui.button("Yeni Malzeme").clicked() {
                    material_dialog.open = true;
                }
            });
            ui.horizontal(|ui| {
                if ui.button("Mesnet Ata").clicked() {
                    restraint_dialog.open = true;
                }
                ui.label("Birlesim Tol.");
                ui.add(egui::DragValue::new(&mut node_merge.tolerance).speed(0.01));
                if ui.button("Dugum Birlestir").clicked() {
                    node_merge.merge_requested = true;
                }
            });
            ui.separator();

            draw_assignment_controls(
                ui,
                &selection,
                &mut project,
                &mut undo_stack,
                &mut model_change,
                &mut section_choice,
                &mut material_choice,
            );
            ui.separator();

            if selection.selected_elements.is_empty() {
                draw_model_summary(ui, &stats, &project);
                return;
            }

            if selection.selected_elements.len() == 1 {
                if let Some(element) = selected_elements.iter().next() {
                    show_single_element(ui, element, &node_map, &project);
                }
            } else {
                ui.label(format!(
                    "{} eleman secili",
                    selection.selected_elements.len()
                ));
            }
        });
}

fn draw_model_summary(ui: &mut egui::Ui, stats: &ModelStats, project: &ProjectResource) {
    ui.label("Eleman secimi yok");
    ui.separator();
    ui.label(format!("Toplam dugum: {}", stats.total_nodes));
    ui.label(format!("Toplam eleman: {}", stats.total_elements));
    ui.label(format!("Secili: {}", stats.selected_count));
    ui.label(format!(
        "Malzeme: {} | Kesit: {}",
        project.project.materials.len(),
        project.project.sections.len()
    ));

    let report = validate_project(&project.project);
    ui.separator();
    ui.label(format!("Dogrulama bulgusu: {}", report.issues.len()));
    for issue in report.issues.iter().take(4) {
        ui.label(format!("- [{}] {}", issue.code, issue.message));
    }
}

fn draw_assignment_controls(
    ui: &mut egui::Ui,
    selection: &SelectionState,
    project: &mut ProjectResource,
    undo_stack: &mut UndoStack,
    model_change: &mut ModelChangeState,
    section_choice: &mut Option<u32>,
    material_choice: &mut Option<u32>,
) {
    if selection.selected_elements.is_empty() {
        ui.label("Atama icin eleman secin.");
        return;
    }

    let mut section_options: Vec<(u32, String)> = project
        .project
        .sections
        .values()
        .map(|s| (s.id, s.name.clone()))
        .collect();
    section_options.sort_by_key(|(id, _)| *id);

    let mut material_options: Vec<(u32, String)> = project
        .project
        .materials
        .values()
        .map(|m| (m.id, m.name.clone()))
        .collect();
    material_options.sort_by_key(|(id, _)| *id);

    ui.label(format!(
        "Secim: {} eleman",
        selection.selected_elements.len()
    ));

    egui::ComboBox::from_label("Kesit")
        .selected_text(match section_choice {
            Some(id) => format!("ID {id}"),
            None => "Atanmamis".to_string(),
        })
        .show_ui(ui, |ui| {
            ui.selectable_value(section_choice, None, "Atanmamis");
            for (id, name) in &section_options {
                ui.selectable_value(section_choice, Some(*id), format!("{id}: {name}"));
            }
        });

    if ui.button("Kesit Ata").clicked() {
        let cmd = AssignSectionCommand::new(selection.selected_elements.clone(), *section_choice);
        if let Err(err) = undo_stack.execute(Box::new(cmd), &mut project.project) {
            warn!("assign section failed: {err:#}");
        } else {
            model_change.dirty = true;
        }
    }

    egui::ComboBox::from_label("Malzeme")
        .selected_text(match material_choice {
            Some(id) => format!("ID {id}"),
            None => "Atanmamis".to_string(),
        })
        .show_ui(ui, |ui| {
            ui.selectable_value(material_choice, None, "Atanmamis");
            for (id, name) in &material_options {
                ui.selectable_value(material_choice, Some(*id), format!("{id}: {name}"));
            }
        });

    if ui.button("Malzeme Ata").clicked() {
        let cmd = AssignMaterialCommand::new(selection.selected_elements.clone(), *material_choice);
        if let Err(err) = undo_stack.execute(Box::new(cmd), &mut project.project) {
            warn!("assign material failed: {err:#}");
        } else {
            model_change.dirty = true;
        }
    }
}

fn show_single_element(
    ui: &mut egui::Ui,
    element: &StructuralElement,
    node_map: &HashMap<u32, Vec3>,
    project: &ProjectResource,
) {
    let ni = node_map.get(&element.node_i).copied().unwrap_or(Vec3::ZERO);
    let nj = node_map.get(&element.node_j).copied().unwrap_or(Vec3::ZERO);
    let length = ni.distance(nj);

    ui.label(format!("Eleman ID: {}", element.id));
    ui.label(format!("Tip: {:?}", element.element_type));
    ui.label(format!("node_i: {}", element.node_i));
    ui.label(format!("node_j: {}", element.node_j));
    ui.separator();
    ui.label(format!("i: ({:.2}, {:.2}, {:.2})", ni.x, ni.y, ni.z));
    ui.label(format!("j: ({:.2}, {:.2}, {:.2})", nj.x, nj.y, nj.z));
    ui.label(format!("Boy: {:.3}", length));
    ui.separator();

    let section = element
        .section_id
        .and_then(|id| project.project.sections.get(&id))
        .map(|s| s.name.clone())
        .unwrap_or_else(|| "Atanmamis".to_string());
    let material = element
        .material_id
        .and_then(|id| project.project.materials.get(&id))
        .map(|m| m.name.clone())
        .unwrap_or_else(|| "Atanmamis".to_string());

    ui.label(format!("Kesit: {}", section));
    ui.label(format!("Malzeme: {}", material));
}
