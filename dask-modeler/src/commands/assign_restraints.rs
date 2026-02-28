//! Assign-restraints command.

use anyhow::Result;

use crate::commands::command::ModelCommand;
use crate::model::Project;

/// Command that assigns the same restraint mask to a set of nodes.
#[derive(Clone, Debug, Default)]
pub struct AssignRestraintsCommand {
    node_ids: Vec<u32>,
    restraints: [bool; 6],
    previous: Vec<(u32, [bool; 6])>,
}

impl AssignRestraintsCommand {
    /// Creates a new assign-restraints command.
    pub fn new(node_ids: Vec<u32>, restraints: [bool; 6]) -> Self {
        Self {
            node_ids,
            restraints,
            previous: Vec::new(),
        }
    }
}

impl ModelCommand for AssignRestraintsCommand {
    fn name(&self) -> &'static str {
        "AssignRestraints"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if self.previous.is_empty() {
            self.previous = self
                .node_ids
                .iter()
                .filter_map(|id| project.nodes.get(id).map(|n| (*id, n.restraints)))
                .collect();
        }

        for node_id in &self.node_ids {
            if let Some(node) = project.nodes.get_mut(node_id) {
                node.restraints = self.restraints;
            }
        }

        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        for (node_id, previous) in &self.previous {
            if let Some(node) = project.nodes.get_mut(node_id) {
                node.restraints = *previous;
            }
        }
        Ok(())
    }
}
