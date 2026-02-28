//! New material creation dialog.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::resources::{NewMaterialDialogState, ProjectResource};
use crate::model::MaterialDef;

/// Draws material-definition dialog and inserts a new material into the project.
pub fn new_material_dialog_ui(
    mut contexts: EguiContexts<'_, '_>,
    mut state: ResMut<'_, NewMaterialDialogState>,
    mut project_res: ResMut<'_, ProjectResource>,
) {
    if !state.open {
        return;
    }

    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    let mut open = state.open;
    let mut should_close = false;
    let mut create_requested = false;

    egui::Window::new("Yeni Malzeme")
        .open(&mut open)
        .resizable(false)
        .show(ctx, |ui| {
            ui.label("Muhendislik malzemesini tanimla");
            ui.horizontal(|ui| {
                ui.label("Ad");
                ui.text_edit_singleline(&mut state.name);
            });

            property_input(ui, "E (MPa)", &mut state.e, 1.0);
            property_input(ui, "G (MPa)", &mut state.g, 1.0);
            property_input(ui, "nu", &mut state.nu, 0.01);
            property_input(ui, "Yogunluk", &mut state.density, 1.0);
            property_input(ui, "fy", &mut state.fy, 1.0);
            property_input(ui, "fu", &mut state.fu, 1.0);

            if ui.button("Balsa Hazir Deger").clicked() {
                let preset = MaterialDef::balsa_default(0);
                state.name = preset.name;
                state.e = preset.e;
                state.g = preset.g;
                state.nu = preset.nu;
                state.density = preset.density;
                state.fy = preset.fy;
                state.fu = preset.fu;
            }

            ui.separator();
            ui.horizontal(|ui| {
                if ui.button("Olustur").clicked() {
                    create_requested = true;
                }
                if ui.button("Iptal").clicked() {
                    should_close = true;
                }
            });
        });

    if create_requested {
        let id = project_res.project.next_material_id;
        let name = if state.name.trim().is_empty() {
            format!("MAT-{id}")
        } else {
            state.name.trim().to_string()
        };
        project_res.project.insert_material(MaterialDef::new(
            id,
            name,
            state.e.max(0.0),
            state.g.max(0.0),
            state.nu,
            state.density.max(0.0),
            state.fy.max(0.0),
            state.fu.max(0.0),
        ));
        should_close = true;
    }

    if should_close {
        open = false;
    }
    state.open = open;
}

fn property_input(ui: &mut egui::Ui, label: &str, value: &mut f64, speed: f64) {
    ui.horizontal(|ui| {
        ui.label(label);
        ui.add(egui::DragValue::new(value).speed(speed));
    });
}
