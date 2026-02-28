//! Modal dialogs for section/material/import/export workflows.

pub mod coordinate_input;
pub mod export;
pub mod import;
pub mod new_material;
pub mod new_section;
pub mod restraint_assignment;

/// Returns whether the dialogs module is linked and available.
pub fn module_ready() -> bool {
    true
}
