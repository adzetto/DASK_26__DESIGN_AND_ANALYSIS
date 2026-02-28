//! Mirror-elements command.

use std::collections::HashMap;

use anyhow::{Result, anyhow};

use crate::commands::command::ModelCommand;
use crate::model::{ElementData, NodeData, Project};

/// Principal planes available for mirror operations.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum MirrorPlane {
    /// Mirror across an XY plane (`z = c`).
    XY,
    /// Mirror across an XZ plane (`y = c`).
    XZ,
    /// Mirror across a YZ plane (`x = c`).
    #[default]
    YZ,
}

/// Command that creates mirrored copies of selected elements.
#[derive(Clone, Debug, Default)]
pub struct MirrorElementsCommand {
    element_ids: Vec<u32>,
    plane: MirrorPlane,
    position: f64,
    template_elements: Vec<ElementData>,
    template_nodes: HashMap<u32, NodeData>,
    created_node_ids: Vec<u32>,
    created_element_ids: Vec<u32>,
}

impl MirrorElementsCommand {
    /// Creates a mirror command for selected element ids.
    pub fn new(element_ids: Vec<u32>, plane: MirrorPlane, position: f64) -> Self {
        Self {
            element_ids,
            plane,
            position,
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
                return Err(anyhow!("cannot mirror missing element {element_id}"));
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

        let mirrored = mirror_coords(
            [new_node.x, new_node.y, new_node.z],
            self.plane,
            self.position,
        );
        new_node.x = mirrored[0];
        new_node.y = mirrored[1];
        new_node.z = mirrored[2];
        new_node.floor = ((new_node.z / 6.0).round().max(0.0)) as u32;

        project.insert_node(new_node);
        self.created_node_ids.push(new_id);
        node_map.insert(source_node_id, new_id);
        Ok(new_id)
    }
}

impl ModelCommand for MirrorElementsCommand {
    fn name(&self) -> &'static str {
        "MirrorElements"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if self.element_ids.is_empty() {
            return Ok(());
        }

        self.build_template_if_needed(project)?;
        self.created_node_ids.clear();
        self.created_element_ids.clear();

        let mut node_map: HashMap<u32, u32> = HashMap::new();
        let templates = self.template_elements.clone();
        for template in templates {
            let node_i = self.map_or_create_node(project, &mut node_map, template.node_i)?;
            let node_j = self.map_or_create_node(project, &mut node_map, template.node_j)?;

            let new_element_id = project.next_element_id;
            let mut mirrored = template.clone();
            mirrored.id = new_element_id;
            mirrored.node_i = node_i;
            mirrored.node_j = node_j;

            let ni = project
                .nodes
                .get(&node_i)
                .ok_or_else(|| anyhow!("mirrored node {} missing", node_i))?;
            let nj = project
                .nodes
                .get(&node_j)
                .ok_or_else(|| anyhow!("mirrored node {} missing", node_j))?;
            let dx = nj.x - ni.x;
            let dy = nj.y - ni.y;
            let dz = nj.z - ni.z;
            mirrored.length = (dx * dx + dy * dy + dz * dz).sqrt();

            project.insert_element(mirrored);
            self.created_element_ids.push(new_element_id);
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

fn mirror_coords(coords: [f64; 3], plane: MirrorPlane, position: f64) -> [f64; 3] {
    match plane {
        MirrorPlane::XY => [coords[0], coords[1], 2.0 * position - coords[2]],
        MirrorPlane::XZ => [coords[0], 2.0 * position - coords[1], coords[2]],
        MirrorPlane::YZ => [2.0 * position - coords[0], coords[1], coords[2]],
    }
}

#[cfg(test)]
mod tests {
    use super::{MirrorElementsCommand, MirrorPlane};
    use crate::commands::command::ModelCommand;
    use crate::model::{ElementData, ElementType, NodeData, Project};

    #[test]
    fn mirror_elements_creates_mirrored_copy_and_undoes() {
        let mut project = Project::new("mirror-test");
        project.insert_node(NodeData::new(1, 2.0, 0.0, 0.0, 0, "tower"));
        project.insert_node(NodeData::new(2, 4.0, 0.0, 0.0, 0, "tower"));
        project.insert_element(ElementData::new(1, 1, 2, ElementType::BeamX, 2.0));

        let mut command = MirrorElementsCommand::new(vec![1], MirrorPlane::YZ, 0.0);
        command
            .execute(&mut project)
            .expect("mirror execute failed");

        assert_eq!(project.elements.len(), 2);
        assert_eq!(project.nodes.len(), 4);

        let mirrored_node = project
            .nodes
            .values()
            .find(|n| (n.x + 2.0).abs() < 1e-9)
            .expect("mirrored node should exist");
        assert_eq!(mirrored_node.y, 0.0);

        command.undo(&mut project).expect("mirror undo failed");
        assert_eq!(project.elements.len(), 1);
        assert_eq!(project.nodes.len(), 2);
    }
}
