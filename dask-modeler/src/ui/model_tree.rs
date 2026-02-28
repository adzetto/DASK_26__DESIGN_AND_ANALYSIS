//! Left-side model tree/filter panel.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::components::ElementType;
use crate::ecs::resources::{ProjectResource, VisibilityFilter};

/// Draws project tree and filtering controls.
pub fn model_tree_ui(
    mut contexts: EguiContexts<'_, '_>,
    project: Res<'_, ProjectResource>,
    mut filter: ResMut<'_, VisibilityFilter>,
) {
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    egui::SidePanel::left("model_tree_panel")
        .default_width(250.0)
        .show(ctx, |ui| {
            ui.heading("Model Agaci");

            ui.collapsing("Malzemeler", |ui| {
                if project.project.materials.is_empty() {
                    ui.label("Malzeme yok");
                } else {
                    for mat in project.project.materials.values() {
                        ui.label(format!("{} ({})", mat.name, mat.id));
                    }
                }
            });

            ui.collapsing("Kesitler", |ui| {
                if project.project.sections.is_empty() {
                    ui.label("Kesit yok");
                } else {
                    for sec in project.project.sections.values() {
                        ui.label(format!("{} ({})", sec.name, sec.id));
                    }
                }
            });

            ui.collapsing("Katlar", |ui| {
                for floor in 0_u32..=25 {
                    let selected = filter.floor == Some(floor);
                    if ui
                        .selectable_label(selected, format!("Kat {}", floor))
                        .clicked()
                    {
                        filter.floor = if selected { None } else { Some(floor) };
                    }
                }
                if ui.button("Kat filtresini temizle").clicked() {
                    filter.floor = None;
                }
            });

            ui.collapsing("Eleman Tipleri", |ui| {
                for (label, ty) in element_type_items() {
                    let selected = filter.element_type.as_ref() == Some(&ty);
                    if ui.selectable_label(selected, label).clicked() {
                        filter.element_type = if selected { None } else { Some(ty) };
                    }
                }
                if ui.button("Tip filtresini temizle").clicked() {
                    filter.element_type = None;
                }
            });
        });
}

fn element_type_items() -> [(String, ElementType); 9] {
    [
        ("beam_x".to_string(), ElementType::BeamX),
        ("beam_y".to_string(), ElementType::BeamY),
        ("column".to_string(), ElementType::Column),
        ("brace_xz".to_string(), ElementType::BraceXZ),
        ("brace_yz".to_string(), ElementType::BraceYZ),
        ("brace_floor".to_string(), ElementType::BraceFloor),
        ("core_wall".to_string(), ElementType::CoreWall),
        ("chevron".to_string(), ElementType::Chevron),
        ("brace_space".to_string(), ElementType::BraceSpace),
    ]
}
