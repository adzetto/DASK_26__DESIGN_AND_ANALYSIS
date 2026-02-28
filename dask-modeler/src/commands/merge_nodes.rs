//! Merge-nodes command.

use std::collections::HashMap;

use anyhow::Result;

use crate::commands::command::ModelCommand;
use crate::model::Project;

/// Command that merges nearby nodes within a tolerance.
#[derive(Clone, Debug, Default)]
pub struct MergeNodesCommand {
    tolerance: f64,
    candidate_node_ids: Option<Vec<u32>>,
    before: Option<Project>,
}

impl MergeNodesCommand {
    /// Creates a merge command with distance tolerance.
    pub fn new(tolerance: f64) -> Self {
        Self {
            tolerance,
            candidate_node_ids: None,
            before: None,
        }
    }

    /// Creates a merge command constrained to specific nodes.
    pub fn new_for_nodes(tolerance: f64, candidate_node_ids: Vec<u32>) -> Self {
        let mut ids = candidate_node_ids;
        ids.sort_unstable();
        ids.dedup();
        Self {
            tolerance,
            candidate_node_ids: Some(ids),
            before: None,
        }
    }
}

impl ModelCommand for MergeNodesCommand {
    fn name(&self) -> &'static str {
        "MergeNodes"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if self.before.is_none() {
            self.before = Some(project.clone());
        }

        let mut ids: Vec<u32> = match &self.candidate_node_ids {
            Some(candidates) => candidates
                .iter()
                .copied()
                .filter(|id| project.nodes.contains_key(id))
                .collect(),
            None => project.nodes.keys().copied().collect(),
        };
        ids.sort_unstable();
        let mut map: HashMap<u32, u32> = HashMap::new();

        for (idx, id_a) in ids.iter().enumerate() {
            let Some(node_a) = project.nodes.get(id_a) else {
                continue;
            };
            for id_b in ids.iter().skip(idx + 1) {
                let Some(node_b) = project.nodes.get(id_b) else {
                    continue;
                };
                let dx = node_b.x - node_a.x;
                let dy = node_b.y - node_a.y;
                let dz = node_b.z - node_a.z;
                let d = (dx * dx + dy * dy + dz * dz).sqrt();
                if d <= self.tolerance {
                    map.insert(*id_b, *id_a);
                }
            }
        }

        if map.is_empty() {
            return Ok(());
        }

        for element in project.elements.values_mut() {
            if let Some(new_i) = map.get(&element.node_i).copied() {
                element.node_i = new_i;
            }
            if let Some(new_j) = map.get(&element.node_j).copied() {
                element.node_j = new_j;
            }
        }

        project.elements.retain(|_, e| e.node_i != e.node_j);
        for remove_id in map.keys() {
            project.nodes.remove(remove_id);
        }

        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        if let Some(before) = &self.before {
            *project = before.clone();
        }
        Ok(())
    }
}
