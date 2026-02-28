//! Egui UI modules and panels.

pub mod dialogs;
pub mod element_table;
pub mod labels_overlay;
pub mod model_tree;
pub mod properties_panel;
pub mod section_plane_controls;
pub mod section_view;
pub mod status_bar;
pub mod theme;
pub mod toolbar;

/// Returns whether the UI module is linked and available.
pub fn module_ready() -> bool {
    true
}
