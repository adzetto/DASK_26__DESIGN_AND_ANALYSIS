//! ECS-independent structural model domain types.

pub mod adjacency;
pub mod connectivity;
pub mod element;
pub mod material;
pub mod node;
pub mod project;
pub mod section;
pub mod validation;

pub use element::{ElementData, ElementType};
pub use material::MaterialDef;
pub use node::NodeData;
pub use project::{Project, Units};
pub use section::{SectionDef, SectionShape};

/// Returns whether the model module is linked and available.
pub fn module_ready() -> bool {
    true
}
