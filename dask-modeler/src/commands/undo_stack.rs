//! Undo stack declarations.

use anyhow::Result;
use bevy::prelude::Resource;

use crate::commands::command::ModelCommand;
use crate::model::Project;

/// Undo/redo stack for project-edit commands.
#[derive(Resource)]
pub struct UndoStack {
    undo: Vec<Box<dyn ModelCommand>>,
    redo: Vec<Box<dyn ModelCommand>>,
    max_size: usize,
}

impl Default for UndoStack {
    fn default() -> Self {
        Self {
            undo: Vec::new(),
            redo: Vec::new(),
            max_size: 500,
        }
    }
}

impl UndoStack {
    /// Executes and records a new command.
    pub fn execute(
        &mut self,
        mut command: Box<dyn ModelCommand>,
        project: &mut Project,
    ) -> Result<()> {
        command.execute(project)?;
        self.undo.push(command);
        self.redo.clear();
        if self.undo.len() > self.max_size {
            let overflow = self.undo.len() - self.max_size;
            self.undo.drain(0..overflow);
        }
        Ok(())
    }

    /// Undoes the latest command.
    pub fn undo(&mut self, project: &mut Project) -> Result<bool> {
        let Some(mut command) = self.undo.pop() else {
            return Ok(false);
        };
        command.undo(project)?;
        self.redo.push(command);
        Ok(true)
    }

    /// Redoes the latest undone command.
    pub fn redo(&mut self, project: &mut Project) -> Result<bool> {
        let Some(mut command) = self.redo.pop() else {
            return Ok(false);
        };
        command.execute(project)?;
        self.undo.push(command);
        Ok(true)
    }

    /// Clears command history.
    pub fn clear(&mut self) {
        self.undo.clear();
        self.redo.clear();
    }

    /// Returns undo command count.
    pub fn undo_len(&self) -> usize {
        self.undo.len()
    }

    /// Returns redo command count.
    pub fn redo_len(&self) -> usize {
        self.redo.len()
    }
}
