//! ECS bridge layer between domain model and Bevy world.

pub mod components;
pub mod events;
pub mod resources;
pub mod systems;

/// Returns whether the ECS module is linked and available.
pub fn module_ready() -> bool {
    true
}
