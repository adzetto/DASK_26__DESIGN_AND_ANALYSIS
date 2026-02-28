//! CSV import helpers for DASK node/element matrices.

use std::path::Path;

use anyhow::{Context, Result};
use serde::Deserialize;

use crate::model::{ElementData, ElementType, NodeData, Project};

#[derive(Deserialize)]
struct PositionRow {
    #[serde(alias = "node_id")]
    node_id: u32,
    #[serde(alias = "x")]
    x: f64,
    #[serde(alias = "y")]
    y: f64,
    #[serde(alias = "z")]
    z: f64,
    #[serde(alias = "floor")]
    floor: u32,
    #[serde(alias = "zone")]
    zone: String,
}

#[derive(Deserialize)]
struct ConnectivityRow {
    #[serde(alias = "element_id")]
    element_id: u32,
    #[serde(alias = "node_i")]
    node_i: u32,
    #[serde(alias = "node_j")]
    node_j: u32,
    #[serde(alias = "element_type")]
    element_type: String,
    #[serde(alias = "length")]
    length: f64,
}

/// Loads `position_matrix.csv` into `NodeData` rows.
pub fn load_position_csv(path: impl AsRef<Path>) -> Result<Vec<NodeData>> {
    let csv_path = path.as_ref();
    let mut reader = csv::Reader::from_path(csv_path)
        .with_context(|| format!("failed to open position csv: {}", csv_path.display()))?;

    reader
        .deserialize::<PositionRow>()
        .map(|row| {
            let row = row.with_context(|| {
                format!(
                    "failed to deserialize row in position csv: {}",
                    csv_path.display()
                )
            })?;
            Ok(NodeData::new(
                row.node_id,
                row.x,
                row.y,
                row.z,
                row.floor,
                row.zone,
            ))
        })
        .collect()
}

/// Loads `connectivity_matrix.csv` into `ElementData` rows.
pub fn load_connectivity_csv(path: impl AsRef<Path>) -> Result<Vec<ElementData>> {
    let csv_path = path.as_ref();
    let mut reader = csv::Reader::from_path(csv_path)
        .with_context(|| format!("failed to open connectivity csv: {}", csv_path.display()))?;

    reader
        .deserialize::<ConnectivityRow>()
        .map(|row| {
            let row = row.with_context(|| {
                format!(
                    "failed to deserialize row in connectivity csv: {}",
                    csv_path.display()
                )
            })?;
            Ok(ElementData::new(
                row.element_id,
                row.node_i,
                row.node_j,
                ElementType::from_str(&row.element_type),
                row.length,
            ))
        })
        .collect()
}

impl Project {
    /// Builds a complete project from node and connectivity CSV matrices.
    pub fn from_csv(pos_path: impl AsRef<Path>, conn_path: impl AsRef<Path>) -> Result<Self> {
        let nodes = load_position_csv(pos_path)?;
        let elements = load_connectivity_csv(conn_path)?;
        let mut project = Project::new("DASK 2026 Model");

        for node in nodes {
            project.insert_node(node);
        }
        for element in elements {
            project.insert_element(element);
        }

        Ok(project)
    }
}
