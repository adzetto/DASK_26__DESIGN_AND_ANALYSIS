//! File IO services for CSV/JSON/export formats.

pub mod csv_io;
pub mod json_project;
pub mod matrix_export;
pub mod opensees_export;

/// Returns whether the IO module is linked and available.
pub fn module_ready() -> bool {
    true
}
