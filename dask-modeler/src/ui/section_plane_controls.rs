//! Section-plane control panel.

use std::collections::BTreeMap;

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::resources::{ProjectResource, SectionPlanes};

/// Draws section-plane enable toggles, offsets, depth, and floor navigation controls.
pub fn section_plane_controls_ui(
    mut contexts: EguiContexts<'_, '_>,
    mut planes: ResMut<'_, SectionPlanes>,
    project: Res<'_, ProjectResource>,
) {
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    let floor_map = floor_to_z_map(&project.project);
    egui::Window::new("Kesit Duzlemleri")
        .default_width(300.0)
        .show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.checkbox(&mut planes.xy_enabled, "XY");
                ui.add(egui::Slider::new(&mut planes.xy_z, 0.0..=160.0).text("Z"));
            });
            ui.horizontal(|ui| {
                ui.checkbox(&mut planes.xz_enabled, "XZ");
                ui.add(egui::Slider::new(&mut planes.xz_y, -20.0..=40.0).text("Y"));
            });
            ui.horizontal(|ui| {
                ui.checkbox(&mut planes.yz_enabled, "YZ");
                ui.add(egui::Slider::new(&mut planes.yz_x, -20.0..=40.0).text("X"));
            });

            ui.separator();
            ui.add(egui::Slider::new(&mut planes.depth, 0.01..=5.0).text("Derinlik"));
            ui.label("Kisayol: Ctrl+1 XY, Ctrl+2 XZ, Ctrl+3 YZ");

            ui.separator();
            ui.label("Kat Gezinti");
            let current_text = planes
                .floor_navigation
                .map(|f| format!("Kat {f}"))
                .unwrap_or_else(|| "Yok".to_string());
            egui::ComboBox::from_label("Aktif kat")
                .selected_text(current_text)
                .show_ui(ui, |ui| {
                    if ui
                        .selectable_label(planes.floor_navigation.is_none(), "Yok")
                        .clicked()
                    {
                        planes.floor_navigation = None;
                    }
                    for (floor, z) in &floor_map {
                        if ui
                            .selectable_label(
                                planes.floor_navigation == Some(*floor),
                                format!("Kat {floor} (z={z:.2})"),
                            )
                            .clicked()
                        {
                            planes.floor_navigation = Some(*floor);
                            planes.xy_enabled = true;
                            planes.xy_z = *z as f32;
                        }
                    }
                });
        });
}

fn floor_to_z_map(project: &crate::model::Project) -> BTreeMap<u32, f64> {
    let mut accumulator: BTreeMap<u32, (f64, usize)> = BTreeMap::new();
    for node in project.nodes.values() {
        let entry = accumulator.entry(node.floor).or_insert((0.0, 0));
        entry.0 += node.z;
        entry.1 += 1;
    }

    accumulator
        .into_iter()
        .map(|(floor, (sum, count))| (floor, sum / count.max(1) as f64))
        .collect()
}
