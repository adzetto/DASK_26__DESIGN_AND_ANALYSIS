//! Move-nodes command.

use std::collections::HashSet;

use anyhow::{Result, anyhow};

use crate::commands::command::ModelCommand;
use crate::model::{NodeData, Project};

/// Command that translates a set of nodes by a fixed delta.
#[derive(Clone, Debug, Default)]
pub struct MoveNodesCommand {
    node_ids: Vec<u32>,
    delta: [f64; 3],
    original_nodes: Vec<NodeData>,
    original_lengths: Vec<(u32, f64)>,
}

impl MoveNodesCommand {
    /// Creates a move command from node ids and translation delta.
    pub fn new(node_ids: Vec<u32>, delta: [f64; 3]) -> Self {
        Self {
            node_ids,
            delta,
            original_nodes: Vec::new(),
            original_lengths: Vec::new(),
        }
    }

    fn capture_original_state(&mut self, project: &Project) -> Result<()> {
        if !self.original_nodes.is_empty() {
            return Ok(());
        }

        for node_id in &self.node_ids {
            let Some(node) = project.nodes.get(node_id) else {
                return Err(anyhow!("cannot move missing node {node_id}"));
            };
            self.original_nodes.push(node.clone());
        }

        let node_set: HashSet<u32> = self.node_ids.iter().copied().collect();
        for element in project.elements.values() {
            if node_set.contains(&element.node_i) || node_set.contains(&element.node_j) {
                self.original_lengths.push((element.id, element.length));
            }
        }

        Ok(())
    }
}

impl ModelCommand for MoveNodesCommand {
    fn name(&self) -> &'static str {
        "MoveNodes"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if self.node_ids.is_empty() {
            return Ok(());
        }

        self.capture_original_state(project)?;

        for node_id in &self.node_ids {
            let Some(node) = project.nodes.get_mut(node_id) else {
                return Err(anyhow!("cannot move missing node {node_id}"));
            };
            node.x += self.delta[0];
            node.y += self.delta[1];
            node.z += self.delta[2];
            node.floor = ((node.z / 6.0).round().max(0.0)) as u32;
        }

        recalculate_connected_lengths(project, &self.node_ids);
        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        for original in &self.original_nodes {
            if let Some(node) = project.nodes.get_mut(&original.id) {
                *node = original.clone();
            }
        }

        for (element_id, original_length) in &self.original_lengths {
            if let Some(element) = project.elements.get_mut(element_id) {
                element.length = *original_length;
            }
        }

        Ok(())
    }
}

fn recalculate_connected_lengths(project: &mut Project, node_ids: &[u32]) {
    let node_set: HashSet<u32> = node_ids.iter().copied().collect();
    let nodes = &project.nodes;

    for element in project.elements.values_mut() {
        if !node_set.contains(&element.node_i) && !node_set.contains(&element.node_j) {
            continue;
        }

        let Some(node_i) = nodes.get(&element.node_i) else {
            continue;
        };
        let Some(node_j) = nodes.get(&element.node_j) else {
            continue;
        };

        let dx = node_j.x - node_i.x;
        let dy = node_j.y - node_i.y;
        let dz = node_j.z - node_i.z;
        element.length = (dx * dx + dy * dy + dz * dz).sqrt();
    }
}

#[cfg(test)]
mod tests {
    use super::MoveNodesCommand;
    use crate::commands::command::ModelCommand;
    use crate::model::{ElementData, ElementType, NodeData, Project};

    #[test]
    fn move_nodes_command_updates_coordinates_and_lengths() {
        let mut project = Project::new("test");
        project.insert_node(NodeData::new(1, 0.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(2, 3.0, 4.0, 0.0, 0, "podium"));
        project.insert_element(ElementData::new(1, 1, 2, ElementType::BeamX, 5.0));

        let mut command = MoveNodesCommand::new(vec![2], [0.0, 0.0, 6.0]);
        command.execute(&mut project).expect("move execute failed");

        let moved = project.nodes.get(&2).expect("node 2 should exist");
        assert_eq!(moved.z, 6.0);
        assert_eq!(moved.floor, 1);

        let length = project
            .elements
            .get(&1)
            .expect("element 1 should exist")
            .length;
        assert!((length - 7.810_249_675_9).abs() < 1e-9);

        command.undo(&mut project).expect("move undo failed");
        let restored = project.nodes.get(&2).expect("node 2 should exist");
        assert_eq!(restored.z, 0.0);
        assert_eq!(restored.floor, 0);
        assert_eq!(
            project
                .elements
                .get(&1)
                .expect("element 1 should exist")
                .length,
            5.0
        );
    }
}
