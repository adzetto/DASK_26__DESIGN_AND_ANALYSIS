//! Bottom status bar panel.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::resources::{ModelStats, SelectionState, SnapSettings};

/// Draws bottom status metrics.
pub fn status_bar_ui(
    mut contexts: EguiContexts<'_, '_>,
    stats: Res<'_, ModelStats>,
    selection: Res<'_, SelectionState>,
    snap: Res<'_, SnapSettings>,
) {
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    egui::TopBottomPanel::bottom("status_bar").show(ctx, |ui| {
        ui.horizontal_wrapped(|ui| {
            ui.label(format!(
                "Imlec: X {:.2} Y {:.2} Z {:.2}",
                stats.cursor_world_pos.x, stats.cursor_world_pos.y, stats.cursor_world_pos.z
            ));
            ui.separator();
            ui.label(format!(
                "Yakala: {}",
                if snap.snap_to_node {
                    "Dugum"
                } else if snap.snap_to_grid {
                    "Izgara"
                } else {
                    "Kapali"
                }
            ));
            ui.separator();
            ui.label(format!(
                "Secili: {}",
                selection.selected_elements.len() + selection.selected_nodes.len()
            ));
            ui.separator();
            ui.label(format!(
                "Toplam: {} dugum, {} eleman",
                stats.total_nodes, stats.total_elements
            ));
        });
    });
}
