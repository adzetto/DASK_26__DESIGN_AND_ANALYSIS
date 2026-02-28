//! Restraint assignment dialog.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::resources::RestraintDialogState;

/// Draws node restraint assignment dialog (6 DOF).
pub fn restraint_assignment_dialog_ui(
    mut contexts: EguiContexts<'_, '_>,
    mut state: ResMut<'_, RestraintDialogState>,
) {
    if !state.open {
        return;
    }

    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    let mut open = state.open;
    let mut should_close = false;

    egui::Window::new("Mesnet Atama")
        .open(&mut open)
        .resizable(false)
        .show(ctx, |ui| {
            ui.label("6 serbestlik derecesi secimi");
            ui.horizontal(|ui| {
                ui.checkbox(&mut state.ux, "Ux");
                ui.checkbox(&mut state.uy, "Uy");
                ui.checkbox(&mut state.uz, "Uz");
            });
            ui.horizontal(|ui| {
                ui.checkbox(&mut state.rx, "Rx");
                ui.checkbox(&mut state.ry, "Ry");
                ui.checkbox(&mut state.rz, "Rz");
            });

            ui.separator();
            ui.horizontal(|ui| {
                if ui.button("Sabit Mesnet").clicked() {
                    state.ux = true;
                    state.uy = true;
                    state.uz = true;
                    state.rx = true;
                    state.ry = true;
                    state.rz = true;
                }
                if ui.button("Serbest").clicked() {
                    state.ux = false;
                    state.uy = false;
                    state.uz = false;
                    state.rx = false;
                    state.ry = false;
                    state.rz = false;
                }
            });

            ui.separator();
            ui.horizontal(|ui| {
                if ui.button("Uygula").clicked() {
                    state.apply_requested = true;
                    should_close = true;
                }
                if ui.button("Iptal").clicked() {
                    should_close = true;
                }
            });
        });

    if should_close {
        open = false;
    }
    state.open = open;
}
