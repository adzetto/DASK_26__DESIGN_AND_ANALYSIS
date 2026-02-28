//! UI theme definitions.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::resources::UiSettings;

/// Applies dark/light theme to egui when settings change.
pub fn apply_ui_theme(
    mut contexts: EguiContexts<'_, '_>,
    settings: Res<'_, UiSettings>,
    mut initialized: Local<'_, bool>,
) {
    if *initialized && !settings.is_changed() {
        return;
    }

    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    if settings.dark_theme {
        let mut visuals = egui::Visuals::dark();
        visuals.panel_fill = egui::Color32::from_rgb(26, 29, 34);
        visuals.widgets.noninteractive.bg_fill = egui::Color32::from_rgb(32, 36, 42);
        visuals.widgets.inactive.bg_fill = egui::Color32::from_rgb(40, 45, 52);
        visuals.widgets.hovered.bg_fill = egui::Color32::from_rgb(52, 60, 70);
        visuals.widgets.active.bg_fill = egui::Color32::from_rgb(68, 82, 96);
        visuals.selection.bg_fill = egui::Color32::from_rgb(42, 112, 180);
        ctx.set_visuals(visuals);
    } else {
        ctx.set_visuals(egui::Visuals::light());
    }

    *initialized = true;
}
