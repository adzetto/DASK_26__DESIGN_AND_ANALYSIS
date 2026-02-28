//! ECS systems for rendering, input, and interactions.

pub mod camera;
pub mod drawing;
pub mod grid;
pub mod input;
pub mod picking;
pub mod render;
pub mod section_cut;
pub mod transform;

/// Returns whether the systems module is linked and available.
pub fn module_ready() -> bool {
    true
}
