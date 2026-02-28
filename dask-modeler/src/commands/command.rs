//! Command trait declarations for undoable model edits.

use anyhow::Result;

use crate::model::Project;

/// Undoable project mutation command.
pub trait ModelCommand: Send + Sync {
    /// Human-readable command name.
    fn name(&self) -> &'static str;

    /// Applies this command to the project.
    fn execute(&mut self, project: &mut Project) -> Result<()>;

    /// Reverts this command from the project.
    fn undo(&mut self, project: &mut Project) -> Result<()>;
}
