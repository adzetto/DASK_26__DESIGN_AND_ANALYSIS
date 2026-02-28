//! Add-element command.

use anyhow::{Result, anyhow};

use crate::commands::command::ModelCommand;
use crate::model::{ElementData, Project};

/// Command that adds one element.
#[derive(Clone, Debug)]
pub struct AddElementCommand {
    element: ElementData,
}

impl AddElementCommand {
    /// Creates an element-add command.
    pub fn new(element: ElementData) -> Self {
        Self { element }
    }
}

impl ModelCommand for AddElementCommand {
    fn name(&self) -> &'static str {
        "AddElement"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if project.elements.contains_key(&self.element.id) {
            return Err(anyhow!("element {} already exists", self.element.id));
        }
        if !project.nodes.contains_key(&self.element.node_i)
            || !project.nodes.contains_key(&self.element.node_j)
        {
            return Err(anyhow!(
                "element {} references missing node(s)",
                self.element.id
            ));
        }
        project.insert_element(self.element.clone());
        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        project.elements.remove(&self.element.id);
        Ok(())
    }
}
