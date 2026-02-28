//! Coordinate input dialog.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};
use log::warn;

use crate::commands::UndoStack;
use crate::ecs::resources::{
    CoordinateInputState, DrawingState, ModelChangeState, ProjectResource, ToolMode,
};
use crate::ecs::systems::drawing::apply_coordinate_input_to_drawing;

/// Draws coordinate-input dialog and applies precise node placement to drawing flow.
pub fn coordinate_input_dialog_ui(
    mut contexts: EguiContexts<'_, '_>,
    mut input_state: ResMut<'_, CoordinateInputState>,
    tool_mode: Res<'_, ToolMode>,
    mut drawing_state: ResMut<'_, DrawingState>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut model_change: ResMut<'_, ModelChangeState>,
) {
    if !input_state.open {
        return;
    }

    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    let mut should_close = false;
    let mut open = input_state.open;
    let mut x = input_state.x;
    let mut y = input_state.y;
    let mut z = input_state.z;
    egui::Window::new("Koordinat Girisi")
        .collapsible(false)
        .resizable(false)
        .open(&mut open)
        .show(ctx, |ui| {
            ui.label("Dugum yerlestirme icin kesin koordinat girin.");
            ui.horizontal(|ui| {
                ui.label("X");
                ui.add(egui::DragValue::new(&mut x).speed(0.1));
            });
            ui.horizontal(|ui| {
                ui.label("Y");
                ui.add(egui::DragValue::new(&mut y).speed(0.1));
            });
            ui.horizontal(|ui| {
                ui.label("Z");
                ui.add(egui::DragValue::new(&mut z).speed(0.1));
            });

            ui.separator();
            ui.horizontal(|ui| {
                if ui.button("Uygula").clicked() {
                    let position = Vec3::new(x as f32, y as f32, z as f32);
                    apply_coordinate_input_to_drawing(
                        position,
                        *tool_mode,
                        &mut drawing_state,
                        &mut project_res,
                        &mut undo_stack,
                        &mut model_change,
                    );
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
    input_state.open = open;
    input_state.x = x;
    input_state.y = y;
    input_state.z = z;

    if !matches!(
        *tool_mode,
        ToolMode::DrawBeam | ToolMode::DrawColumn | ToolMode::DrawBrace
    ) && input_state.open
    {
        warn!("coordinate input opened while not in draw mode");
    }
}
