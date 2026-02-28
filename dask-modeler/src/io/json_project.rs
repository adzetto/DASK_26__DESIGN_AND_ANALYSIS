//! JSON project persistence operations.

use std::fs;
use std::path::Path;

use anyhow::{Context, Result};

use crate::model::Project;

/// Loads a full project from a JSON file.
pub fn load_project_json(path: impl AsRef<Path>) -> Result<Project> {
    let json_path = path.as_ref();
    let text = fs::read_to_string(json_path)
        .with_context(|| format!("failed to read json project: {}", json_path.display()))?;
    let project = serde_json::from_str::<Project>(&text)
        .with_context(|| format!("failed to parse json project: {}", json_path.display()))?;
    Ok(project)
}

/// Saves a full project to a JSON file.
pub fn save_project_json(project: &Project, path: impl AsRef<Path>) -> Result<()> {
    let json_path = path.as_ref();
    if let Some(parent) = json_path.parent()
        && !parent.as_os_str().is_empty()
    {
        fs::create_dir_all(parent).with_context(|| {
            format!(
                "failed to create parent directory for json project: {}",
                parent.display()
            )
        })?;
    }

    let content =
        serde_json::to_string_pretty(project).context("failed to serialize project to json")?;
    fs::write(json_path, content)
        .with_context(|| format!("failed to write json project: {}", json_path.display()))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::fs;
    use std::time::{SystemTime, UNIX_EPOCH};

    use crate::io::json_project::{load_project_json, save_project_json};
    use crate::model::{ElementData, ElementType, NodeData, Project};

    #[test]
    fn json_round_trip_preserves_nodes_and_elements() {
        let mut project = Project::new("json-test");
        project.insert_node(NodeData::new(1, 0.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(2, 2.0, 0.0, 0.0, 0, "podium"));
        project.insert_element(ElementData::new(1, 1, 2, ElementType::BeamX, 2.0));

        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock before unix epoch")
            .as_millis();
        let path = std::env::temp_dir().join(format!("dask_modeler_roundtrip_{stamp}.json"));

        save_project_json(&project, &path).expect("save json should succeed");
        let loaded = load_project_json(&path).expect("load json should succeed");
        fs::remove_file(&path).expect("temp json file should be removable");

        assert_eq!(loaded.nodes.len(), 2);
        assert_eq!(loaded.elements.len(), 1);
        assert_eq!(loaded.name, "json-test");
    }
}
