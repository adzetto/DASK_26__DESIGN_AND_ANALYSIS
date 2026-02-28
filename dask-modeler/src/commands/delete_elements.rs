//! Delete-elements command.

use std::collections::HashSet;

use anyhow::Result;

use crate::commands::command::ModelCommand;
use crate::model::{ElementData, NodeData, Project};

/// Command that deletes selected elements and removes orphaned nodes.
#[derive(Clone, Debug, Default)]
pub struct DeleteElementsCommand {
    element_ids: Vec<u32>,
    removed_elements: Vec<ElementData>,
    removed_orphan_nodes: Vec<NodeData>,
}

impl DeleteElementsCommand {
    /// Creates a delete command from element ids.
    pub fn new(element_ids: Vec<u32>) -> Self {
        Self {
            element_ids,
            removed_elements: Vec::new(),
            removed_orphan_nodes: Vec::new(),
        }
    }
}

impl ModelCommand for DeleteElementsCommand {
    fn name(&self) -> &'static str {
        "DeleteElements"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        self.removed_elements.clear();
        self.removed_orphan_nodes.clear();

        let mut touched_node_ids: HashSet<u32> = HashSet::new();
        for id in &self.element_ids {
            if let Some(element) = project.elements.remove(id) {
                touched_node_ids.insert(element.node_i);
                touched_node_ids.insert(element.node_j);
                self.removed_elements.push(element);
            }
        }

        let referenced_nodes: HashSet<u32> = project
            .elements
            .values()
            .flat_map(|e| [e.node_i, e.node_j])
            .collect();

        for node_id in touched_node_ids {
            if !referenced_nodes.contains(&node_id)
                && let Some(node) = project.nodes.remove(&node_id)
            {
                self.removed_orphan_nodes.push(node);
            }
        }

        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        for node in &self.removed_orphan_nodes {
            project.insert_node(node.clone());
        }
        for element in &self.removed_elements {
            project.insert_element(element.clone());
        }
        Ok(())
    }
}
