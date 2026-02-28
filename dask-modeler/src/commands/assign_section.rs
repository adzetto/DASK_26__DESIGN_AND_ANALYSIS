//! Assign-section command.

use anyhow::Result;

use crate::commands::command::ModelCommand;
use crate::model::Project;

/// Command that assigns one section id to many elements.
#[derive(Clone, Debug, Default)]
pub struct AssignSectionCommand {
    element_ids: Vec<u32>,
    section_id: Option<u32>,
    previous: Vec<(u32, Option<u32>)>,
}

impl AssignSectionCommand {
    /// Creates an assign-section command.
    pub fn new(element_ids: Vec<u32>, section_id: Option<u32>) -> Self {
        Self {
            element_ids,
            section_id,
            previous: Vec::new(),
        }
    }
}

impl ModelCommand for AssignSectionCommand {
    fn name(&self) -> &'static str {
        "AssignSection"
    }

    fn execute(&mut self, project: &mut Project) -> Result<()> {
        if self.previous.is_empty() {
            self.previous = self
                .element_ids
                .iter()
                .filter_map(|id| project.elements.get(id).map(|e| (*id, e.section_id)))
                .collect();
        }

        for element_id in &self.element_ids {
            if let Some(element) = project.elements.get_mut(element_id) {
                element.section_id = self.section_id;
            }
        }
        Ok(())
    }

    fn undo(&mut self, project: &mut Project) -> Result<()> {
        for (element_id, previous_section) in &self.previous {
            if let Some(element) = project.elements.get_mut(element_id) {
                element.section_id = *previous_section;
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use crate::commands::assign_section::AssignSectionCommand;
    use crate::commands::command::ModelCommand;
    use crate::model::{ElementData, ElementType, NodeData, Project};

    #[test]
    fn assign_section_command_round_trip() {
        let mut project = Project::new("assign-section");
        project.insert_node(NodeData::new(1, 0.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(2, 1.0, 0.0, 0.0, 0, "podium"));
        project.insert_element(ElementData::new(1, 1, 2, ElementType::BeamX, 1.0));

        let mut cmd = AssignSectionCommand::new(vec![1], Some(12));
        cmd.execute(&mut project).expect("execute should succeed");
        assert_eq!(
            project.elements.get(&1).expect("element exists").section_id,
            Some(12)
        );

        cmd.undo(&mut project).expect("undo should succeed");
        assert_eq!(
            project.elements.get(&1).expect("element exists").section_id,
            None
        );
    }
}
