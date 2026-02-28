//! Command pattern modules for undo/redo operations.

pub mod add_element;
pub mod add_node;
pub mod assign_material;
pub mod assign_restraints;
pub mod assign_section;
pub mod command;
pub mod copy_elements;
pub mod delete_elements;
pub mod merge_nodes;
pub mod mirror_elements;
pub mod move_nodes;
pub mod undo_stack;

pub use add_element::AddElementCommand;
pub use add_node::AddNodeCommand;
pub use assign_material::AssignMaterialCommand;
pub use assign_restraints::AssignRestraintsCommand;
pub use assign_section::AssignSectionCommand;
pub use command::ModelCommand;
pub use copy_elements::CopyElementsCommand;
pub use delete_elements::DeleteElementsCommand;
pub use merge_nodes::MergeNodesCommand;
pub use mirror_elements::{MirrorElementsCommand, MirrorPlane};
pub use move_nodes::MoveNodesCommand;
pub use undo_stack::UndoStack;

/// Returns whether the commands module is linked and available.
pub fn module_ready() -> bool {
    true
}
