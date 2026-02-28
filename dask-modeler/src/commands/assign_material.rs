//! Assign-material command.

use anyhow::Result;

use crate::commands::command::ModelCommand;
use crate::model::Project;

/// Command that assigns one material id to many elements.
#[derive(Clone, Debug, Default)]
pub struct AssignMaterialCommand {
    element_ids: Vec<u32>,
    material_id: Option<u32>,
    previous: Vec<(u32, Option<u32>)>,
}

impl AssignMaterialCommand {
    /// Creates an assign-material command.
    pub fn new(element_ids: Vec<u32>, material_id: Option<u32>) -> Self {
        Self {
            element_ids,
            material_id,
            previous: Vec::new(),
        }
    }
}

impl ModelCommand for AssignMaterialCommand {
    fn name(&self) -> &'static str {
        "AssignMaterial"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if self.previous.is_empty() {
            self.previous = self
                .element_ids
                .iter()
                .filter_map(|id| project.elements.get(id).map(|e| (*id, e.material_id)))
                .collect();
        }

        for element_id in &self.element_ids {
            if let Some(element) = project.elements.get_mut(element_id) {
                element.material_id = self.material_id;
            }
        }
        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        for (element_id, previous_material) in &self.previous {
            if let Some(element) = project.elements.get_mut(element_id) {
                element.material_id = *previous_material;
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use crate::commands::assign_material::AssignMaterialCommand;
    use crate::commands::command::ModelCommand;
    use crate::model::{ElementData, ElementType, NodeData, Project};

    #[test]
    fn assign_material_command_round_trip() {
        let mut project = Project::new("assign-material");
        project.insert_node(NodeData::new(1, 0.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(2, 1.0, 0.0, 0.0, 0, "podium"));
        project.insert_element(ElementData::new(1, 1, 2, ElementType::BeamX, 1.0));

        let mut cmd = AssignMaterialCommand::new(vec![1], Some(7));
        cmd.execute(&mut project).expect("execute should succeed");
        assert_eq!(
            project
                .elements
                .get(&1)
                .expect("element exists")
                .material_id,
            Some(7)
        );

        cmd.undo(&mut project).expect("undo should succeed");
        assert_eq!(
            project
                .elements
                .get(&1)
                .expect("element exists")
                .material_id,
            None
        );
    }
}
