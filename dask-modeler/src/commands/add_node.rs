//! Add-node command.

use anyhow::{Result, anyhow};

use crate::commands::command::ModelCommand;
use crate::model::{NodeData, Project};

/// Command that adds one node.
#[derive(Clone, Debug)]
pub struct AddNodeCommand {
    node: NodeData,
}

impl AddNodeCommand {
    /// Creates a node-add command.
    pub fn new(node: NodeData) -> Self {
        Self { node }
    }
}

impl ModelCommand for AddNodeCommand {
    fn name(&self) -> &'static str {
        "AddNode"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if project.nodes.contains_key(&self.node.id) {
            return Err(anyhow!("node {} already exists", self.node.id));
        }
        project.insert_node(self.node.clone());
        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        project.nodes.remove(&self.node.id);
        Ok(())
    }
}
