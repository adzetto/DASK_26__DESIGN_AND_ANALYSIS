//! Matrix export operations.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use anyhow::{Context, Result};

use crate::model::Project;

/// Exports connectivity matrix rows (element-to-node connectivity) as CSV.
pub fn export_connectivity_csv(project: &Project, path: impl AsRef<Path>) -> Result<()> {
    let csv_path = path.as_ref();
    let mut writer = csv::Writer::from_path(csv_path).with_context(|| {
        format!(
            "failed to create connectivity export csv: {}",
            csv_path.display()
        )
    })?;

    writer.write_record(["element_id", "node_i", "node_j", "element_type", "length"])?;

    let mut ids: Vec<u32> = project.elements.keys().copied().collect();
    ids.sort_unstable();
    for id in ids {
        let Some(element) = project.elements.get(&id) else {
            continue;
        };
        writer.write_record(vec![
            element.id.to_string(),
            element.node_i.to_string(),
            element.node_j.to_string(),
            element.element_type.as_str().to_string(),
            format!("{:.6}", element.length),
        ])?;
    }

    writer.flush()?;
    Ok(())
}

/// Exports dense adjacency matrix CSV (node_id + N columns).
pub fn export_adjacency_dense_csv(project: &Project, path: impl AsRef<Path>) -> Result<()> {
    let csv_path = path.as_ref();
    let mut writer = csv::Writer::from_path(csv_path).with_context(|| {
        format!(
            "failed to create dense adjacency export csv: {}",
            csv_path.display()
        )
    })?;

    let node_ids = sorted_node_ids(project);
    let index_map: BTreeMap<u32, usize> = node_ids
        .iter()
        .enumerate()
        .map(|(i, id)| (*id, i))
        .collect();
    let mut matrix = vec![vec![0_u8; node_ids.len()]; node_ids.len()];

    for element in project.elements.values() {
        let Some(i) = index_map.get(&element.node_i).copied() else {
            continue;
        };
        let Some(j) = index_map.get(&element.node_j).copied() else {
            continue;
        };
        matrix[i][j] = 1;
        matrix[j][i] = 1;
    }

    let mut header = vec!["node_id".to_string()];
    header.extend(node_ids.iter().map(u32::to_string));
    writer.write_record(header)?;

    for (row_idx, row_node_id) in node_ids.iter().enumerate() {
        let mut row = vec![row_node_id.to_string()];
        row.extend(matrix[row_idx].iter().map(u8::to_string));
        writer.write_record(row)?;
    }

    writer.flush()?;
    Ok(())
}

/// Exports sparse adjacency in CSR arrays encoded as CSV rows.
pub fn export_adjacency_sparse_csr_csv(project: &Project, path: impl AsRef<Path>) -> Result<()> {
    let csv_path = path.as_ref();
    let mut writer = csv::Writer::from_path(csv_path).with_context(|| {
        format!(
            "failed to create sparse adjacency export csv: {}",
            csv_path.display()
        )
    })?;

    let node_ids = sorted_node_ids(project);
    let index_map: BTreeMap<u32, usize> = node_ids
        .iter()
        .enumerate()
        .map(|(i, id)| (*id, i))
        .collect();
    let mut rows: Vec<BTreeSet<usize>> = vec![BTreeSet::new(); node_ids.len()];

    for element in project.elements.values() {
        let Some(i) = index_map.get(&element.node_i).copied() else {
            continue;
        };
        let Some(j) = index_map.get(&element.node_j).copied() else {
            continue;
        };
        rows[i].insert(j);
        rows[j].insert(i);
    }

    let mut row_ptr: Vec<usize> = Vec::with_capacity(node_ids.len() + 1);
    let mut col_idx: Vec<usize> = Vec::new();
    let mut values: Vec<u8> = Vec::new();
    row_ptr.push(0);

    for row in &rows {
        for &col in row {
            col_idx.push(col);
            values.push(1);
        }
        row_ptr.push(col_idx.len());
    }

    writer.write_record(["array", "index", "value"])?;
    for (index, value) in row_ptr.iter().enumerate() {
        writer.write_record(vec![
            "row_ptr".to_string(),
            index.to_string(),
            value.to_string(),
        ])?;
    }
    for (index, value) in col_idx.iter().enumerate() {
        writer.write_record(vec![
            "col_idx".to_string(),
            index.to_string(),
            value.to_string(),
        ])?;
    }
    for (index, value) in values.iter().enumerate() {
        writer.write_record(vec![
            "values".to_string(),
            index.to_string(),
            value.to_string(),
        ])?;
    }

    writer.flush()?;
    Ok(())
}

fn sorted_node_ids(project: &Project) -> Vec<u32> {
    let mut node_ids: Vec<u32> = project.nodes.keys().copied().collect();
    node_ids.sort_unstable();
    node_ids
}

#[cfg(test)]
mod tests {
    use std::fs;
    use std::time::{SystemTime, UNIX_EPOCH};

    use crate::io::matrix_export::{
        export_adjacency_dense_csv, export_adjacency_sparse_csr_csv, export_connectivity_csv,
    };
    use crate::model::{ElementData, ElementType, NodeData, Project};

    fn sample_project() -> Project {
        let mut project = Project::new("matrix-test");
        project.insert_node(NodeData::new(1, 0.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(2, 1.0, 0.0, 0.0, 0, "podium"));
        project.insert_node(NodeData::new(3, 1.0, 1.0, 0.0, 0, "podium"));
        project.insert_element(ElementData::new(1, 1, 2, ElementType::BeamX, 1.0));
        project.insert_element(ElementData::new(2, 2, 3, ElementType::BeamY, 1.0));
        project
    }

    fn temp_file(name: &str) -> std::path::PathBuf {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock before unix epoch")
            .as_millis();
        std::env::temp_dir().join(format!("{name}_{stamp}.csv"))
    }

    #[test]
    fn connectivity_export_writes_rows() {
        let project = sample_project();
        let path = temp_file("connectivity_export");
        export_connectivity_csv(&project, &path).expect("export connectivity should succeed");
        let text = fs::read_to_string(&path).expect("exported csv should be readable");
        fs::remove_file(&path).expect("temp connectivity csv should be removable");
        assert!(text.contains("element_id,node_i,node_j,element_type,length"));
        assert!(text.contains("1,1,2,beam_x"));
    }

    #[test]
    fn dense_and_sparse_adjacency_exports_write_content() {
        let project = sample_project();

        let dense_path = temp_file("adj_dense");
        export_adjacency_dense_csv(&project, &dense_path)
            .expect("export dense adjacency should succeed");
        let dense_text =
            fs::read_to_string(&dense_path).expect("dense adjacency csv should be readable");
        fs::remove_file(&dense_path).expect("temp dense csv should be removable");
        assert!(dense_text.contains("node_id,1,2,3"));

        let sparse_path = temp_file("adj_sparse");
        export_adjacency_sparse_csr_csv(&project, &sparse_path)
            .expect("export sparse adjacency should succeed");
        let sparse_text =
            fs::read_to_string(&sparse_path).expect("sparse adjacency csv should be readable");
        fs::remove_file(&sparse_path).expect("temp sparse csv should be removable");
        assert!(sparse_text.contains("array,index,value"));
        assert!(sparse_text.contains("row_ptr"));
        assert!(sparse_text.contains("col_idx"));
    }
}
