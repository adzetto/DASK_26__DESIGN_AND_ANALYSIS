//! Copy-elements command.

use std::collections::HashMap;

use anyhow::{Result, anyhow};

use crate::commands::command::ModelCommand;
use crate::model::{ElementData, NodeData, Project};

/// Command that copies selected elements by an offset.
#[derive(Clone, Debug, Default)]
pub struct CopyElementsCommand {
    element_ids: Vec<u32>,
    offset: [f64; 3],
    repeats: u32,
    template_elements: Vec<ElementData>,
    template_nodes: HashMap<u32, NodeData>,
    created_node_ids: Vec<u32>,
    created_element_ids: Vec<u32>,
}

impl CopyElementsCommand {
    /// Creates a copy command with optional linear-array repetitions.
    pub fn new(element_ids: Vec<u32>, offset: [f64; 3], repeats: u32) -> Self {
        Self {
            element_ids,
            offset,
            repeats,
            template_elements: Vec::new(),
            template_nodes: HashMap::new(),
            created_node_ids: Vec::new(),
            created_element_ids: Vec::new(),
        }
    }

    fn build_template_if_needed(&mut self, project: &Project) -> Result<()> {
        if !self.template_elements.is_empty() {
            return Ok(());
        }

        for element_id in &self.element_ids {
            let Some(element) = project.elements.get(element_id) else {
                return Err(anyhow!("cannot copy missing element {element_id}"));
            };
            self.template_elements.push(element.clone());
        }

        for element in &self.template_elements {
            for node_id in [element.node_i, element.node_j] {
                if self.template_nodes.contains_key(&node_id) {
                    continue;
                }
                let Some(node) = project.nodes.get(&node_id) else {
                    return Err(anyhow!(
                        "element {} references missing node {}",
                        element.id,
                        node_id
                    ));
                };
                self.template_nodes.insert(node_id, node.clone());
            }
        }

        Ok(())
    }

    fn map_or_create_node(
        &mut self,
        project: &mut Project,
        node_map: &mut HashMap<u32, u32>,
        source_node_id: u32,
        translation: [f64; 3],
    ) -> Result<u32> {
        if let Some(existing) = node_map.get(&source_node_id).copied() {
            return Ok(existing);
        }

        let Some(template) = self.template_nodes.get(&source_node_id) else {
            return Err(anyhow!("missing node template for {}", source_node_id));
        };

        let new_id = project.next_node_id;
        let mut new_node = template.clone();
        new_node.id = new_id;
        new_node.x += translation[0];
        new_node.y += translation[1];
        new_node.z += translation[2];
        new_node.floor = ((new_node.z / 6.0).round().max(0.0)) as u32;

        project.insert_node(new_node);
        self.created_node_ids.push(new_id);
        node_map.insert(source_node_id, new_id);
        Ok(new_id)
    }
}

impl ModelCommand for CopyElementsCommand {
    fn name(&self) -> &'static str {
        "CopyElements"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if self.element_ids.is_empty() || self.repeats == 0 {
            return Ok(());
        }

        self.build_template_if_needed(project)?;
        self.created_node_ids.clear();
        self.created_element_ids.clear();

        for repeat in 1..=self.repeats {
            let factor = repeat as f64;
            let translation = [
                self.offset[0] * factor,
                self.offset[1] * factor,
                self.offset[2] * factor,
            ];
            let mut node_map: HashMap<u32, u32> = HashMap::new();

            let templates = self.template_elements.clone();
            for template in templates {
                let node_i =
                    self.map_or_create_node(project, &mut node_map, template.node_i, translation)?;
                let node_j =
                    self.map_or_create_node(project, &mut node_map, template.node_j, translation)?;

                let new_element_id = project.next_element_id;
                let mut copied = template.clone();
                copied.id = new_element_id;
                copied.node_i = node_i;
                copied.node_j = node_j;

                let ni = project
                    .nodes
                    .get(&node_i)
                    .ok_or_else(|| anyhow!("new node {} missing after copy", node_i))?;
                let nj = project
                    .nodes
                    .get(&node_j)
                    .ok_or_else(|| anyhow!("new node {} missing after copy", node_j))?;
                let dx = nj.x - ni.x;
                let dy = nj.y - ni.y;
                let dz = nj.z - ni.z;
                copied.length = (dx * dx + dy * dy + dz * dz).sqrt();

                project.insert_element(copied);
                self.created_element_ids.push(new_element_id);
            }
        }

        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        for element_id in &self.created_element_ids {
            project.elements.remove(element_id);
        }
        for node_id in &self.created_node_ids {
            project.nodes.remove(node_id);
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::CopyElementsCommand;
    use crate::commands::command::ModelCommand;
    use crate::model::{ElementData, ElementType, NodeData, Project};

    #[test]
    fn copy_elements_command_creates_offset_array_and_undoes() {
        let mut project = Project::new("copy-test");
        project.insert_node(NodeData::new(1, 0.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(2, 1.0, 0.0, 0.0, 0, "podium"));
        project.insert_element(ElementData::new(1, 1, 2, ElementType::BeamX, 1.0));

        let mut command = CopyElementsCommand::new(vec![1], [0.0, 0.0, 6.0], 2);
        command.execute(&mut project).expect("copy execute failed");

        assert_eq!(project.elements.len(), 3);
        assert_eq!(project.nodes.len(), 6);

        command.undo(&mut project).expect("copy undo failed");
        assert_eq!(project.elements.len(), 1);
        assert_eq!(project.nodes.len(), 2);
    }
}
