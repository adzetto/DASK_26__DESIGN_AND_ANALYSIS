//! Project aggregate data model, independent from ECS.

use std::collections::HashMap;

use serde::{Deserialize, Serialize};

use crate::model::element::ElementData;
use crate::model::material::MaterialDef;
use crate::model::node::NodeData;
use crate::model::section::SectionDef;

/// Unit metadata used for engineering values.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct Units {
    /// Length unit label.
    pub length: String,
    /// Force unit label.
    pub force: String,
    /// Mass unit label.
    pub mass: String,
}

impl Default for Units {
    fn default() -> Self {
        Self {
            length: "cm".to_string(),
            force: "N".to_string(),
            mass: "kg".to_string(),
        }
    }
}

/// Master container for all model data.
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Project {
    /// Project name.
    pub name: String,
    /// Project schema/version tag.
    pub version: String,
    /// Unit metadata.
    pub units: Units,
    /// Structural nodes by id.
    pub nodes: HashMap<u32, NodeData>,
    /// Structural elements by id.
    pub elements: HashMap<u32, ElementData>,
    /// Section definitions by id.
    pub sections: HashMap<u32, SectionDef>,
    /// Material definitions by id.
    pub materials: HashMap<u32, MaterialDef>,
    /// Next auto node id.
    pub next_node_id: u32,
    /// Next auto element id.
    pub next_element_id: u32,
    /// Next auto section id.
    pub next_section_id: u32,
    /// Next auto material id.
    pub next_material_id: u32,
}

impl Default for Project {
    fn default() -> Self {
        Self::new("DASK Model")
    }
}

impl Project {
    /// Creates an empty project with initialized counters.
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            version: "0.1.0".to_string(),
            units: Units::default(),
            nodes: HashMap::new(),
            elements: HashMap::new(),
            sections: HashMap::new(),
            materials: HashMap::new(),
            next_node_id: 1,
            next_element_id: 1,
            next_section_id: 1,
            next_material_id: 1,
        }
    }

    /// Inserts a node and keeps auto-id counters consistent.
    pub fn insert_node(&mut self, node: NodeData) {
        self.next_node_id = self.next_node_id.max(node.id.saturating_add(1));
        self.nodes.insert(node.id, node);
    }

    /// Inserts an element and keeps auto-id counters consistent.
    pub fn insert_element(&mut self, element: ElementData) {
        self.next_element_id = self.next_element_id.max(element.id.saturating_add(1));
        self.elements.insert(element.id, element);
    }

    /// Inserts a section and keeps auto-id counters consistent.
    pub fn insert_section(&mut self, section: SectionDef) {
        self.next_section_id = self.next_section_id.max(section.id.saturating_add(1));
        self.sections.insert(section.id, section);
    }

    /// Inserts a material and keeps auto-id counters consistent.
    pub fn insert_material(&mut self, material: MaterialDef) {
        self.next_material_id = self.next_material_id.max(material.id.saturating_add(1));
        self.materials.insert(material.id, material);
    }

    /// Returns model bounds as ((xmin,ymin,zmin), (xmax,ymax,zmax)).
    pub fn bounds(&self) -> Option<([f64; 3], [f64; 3])> {
        let mut iter = self.nodes.values();
        let first = iter.next()?;
        let mut min = [first.x, first.y, first.z];
        let mut max = min;

        for node in iter {
            min[0] = min[0].min(node.x);
            min[1] = min[1].min(node.y);
            min[2] = min[2].min(node.z);
            max[0] = max[0].max(node.x);
            max[1] = max[1].max(node.y);
            max[2] = max[2].max(node.z);
        }

        Some((min, max))
    }
}

#[cfg(test)]
mod tests {
    use super::Project;
    use crate::model::node::NodeData;

    #[test]
    fn insert_updates_next_ids() {
        let mut project = Project::new("Test");
        project.insert_node(NodeData::new(5, 0.0, 0.0, 0.0, 0, "podium"));
        assert_eq!(project.next_node_id, 6);
    }
}
