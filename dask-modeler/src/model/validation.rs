//! Model validation helpers.

use std::collections::{HashMap, HashSet};

use serde::{Deserialize, Serialize};

use crate::model::Project;

/// Severity of a validation finding.
#[derive(Serialize, Deserialize, Clone, Copy, Debug, PartialEq, Eq)]
pub enum ValidationSeverity {
    Error,
    Warning,
    Info,
}

/// A model validation finding.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct ValidationIssue {
    pub severity: ValidationSeverity,
    pub code: String,
    pub message: String,
}

/// Summary report from model validation.
#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct ValidationReport {
    pub issues: Vec<ValidationIssue>,
}

impl ValidationReport {
    /// Returns true if report has at least one error.
    pub fn has_errors(&self) -> bool {
        self.issues
            .iter()
            .any(|i| i.severity == ValidationSeverity::Error)
    }
}

/// Runs core model validation checks.
pub fn validate_project(project: &Project) -> ValidationReport {
    let mut issues = Vec::new();
    issues.extend(check_orphan_nodes(project));
    issues.extend(check_zero_length_elements(project));
    issues.extend(check_missing_section_assignments(project));
    ValidationReport { issues }
}

fn check_orphan_nodes(project: &Project) -> Vec<ValidationIssue> {
    let mut referenced: HashSet<u32> = HashSet::new();
    for element in project.elements.values() {
        referenced.insert(element.node_i);
        referenced.insert(element.node_j);
    }

    let mut orphan_ids: Vec<u32> = project
        .nodes
        .keys()
        .copied()
        .filter(|id| !referenced.contains(id))
        .collect();
    orphan_ids.sort_unstable();

    if orphan_ids.is_empty() {
        return Vec::new();
    }

    vec![ValidationIssue {
        severity: ValidationSeverity::Warning,
        code: "ORPHAN_NODE".to_string(),
        message: format!("Bağlantısız düğümler: {:?}", orphan_ids),
    }]
}

fn check_zero_length_elements(project: &Project) -> Vec<ValidationIssue> {
    let mut bad_ids: Vec<u32> = Vec::new();
    for element in project.elements.values() {
        let Some(node_i) = project.nodes.get(&element.node_i) else {
            continue;
        };
        let Some(node_j) = project.nodes.get(&element.node_j) else {
            continue;
        };
        let dx = node_j.x - node_i.x;
        let dy = node_j.y - node_i.y;
        let dz = node_j.z - node_i.z;
        let length = (dx * dx + dy * dy + dz * dz).sqrt();
        if length <= 1e-9 {
            bad_ids.push(element.id);
        }
    }
    bad_ids.sort_unstable();

    if bad_ids.is_empty() {
        return Vec::new();
    }

    vec![ValidationIssue {
        severity: ValidationSeverity::Error,
        code: "ZERO_LENGTH".to_string(),
        message: format!("Sıfır boy elemanlar: {:?}", bad_ids),
    }]
}

fn check_missing_section_assignments(project: &Project) -> Vec<ValidationIssue> {
    let mut per_type_missing: HashMap<String, usize> = HashMap::new();
    for element in project.elements.values() {
        if element.section_id.is_none() {
            *per_type_missing
                .entry(element.element_type.as_str().to_string())
                .or_insert(0) += 1;
        }
    }

    if per_type_missing.is_empty() {
        return Vec::new();
    }

    let mut parts: Vec<String> = per_type_missing
        .into_iter()
        .map(|(t, count)| format!("{t}:{count}"))
        .collect();
    parts.sort();

    vec![ValidationIssue {
        severity: ValidationSeverity::Info,
        code: "MISSING_SECTION".to_string(),
        message: format!("Kesit atanmamış elemanlar ({})", parts.join(", ")),
    }]
}

#[cfg(test)]
mod tests {
    use crate::model::{ElementData, ElementType, NodeData, Project, validation::validate_project};

    #[test]
    fn detects_orphans_and_zero_length() {
        let mut project = Project::new("validation");
        project.insert_node(NodeData::new(1, 0.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(2, 0.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(3, 10.0, 0.0, 0.0, 0, "podium"));
        project.insert_element(ElementData::new(1, 1, 2, ElementType::BeamX, 0.0));

        let report = validate_project(&project);
        assert!(report.issues.iter().any(|i| i.code == "ORPHAN_NODE"));
        assert!(report.issues.iter().any(|i| i.code == "ZERO_LENGTH"));
    }
}
