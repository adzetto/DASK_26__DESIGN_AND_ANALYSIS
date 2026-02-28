//! IO module integration tests.

use std::path::PathBuf;

use dask_modeler::io::csv_io::{load_connectivity_csv, load_position_csv};
use dask_modeler::model::Project;

fn dask_data_dir() -> PathBuf {
    if let Ok(dir) = std::env::var("DASK_DATA_DIR") {
        return PathBuf::from(dir);
    }
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("data")
}

#[test]
fn loads_position_matrix_with_expected_count() {
    let path = dask_data_dir().join("position_matrix.csv");
    let nodes = load_position_csv(path).expect("position csv should load");
    assert_eq!(nodes.len(), 442);
}

#[test]
fn loads_connectivity_matrix_with_expected_count() {
    let path = dask_data_dir().join("connectivity_matrix.csv");
    let elements = load_connectivity_csv(path).expect("connectivity csv should load");
    assert_eq!(elements.len(), 2138);
}

#[test]
fn builds_project_from_csv_with_expected_counts() {
    let data = dask_data_dir();
    let project = Project::from_csv(
        data.join("position_matrix.csv"),
        data.join("connectivity_matrix.csv"),
    )
    .expect("project should build from csv");

    assert_eq!(project.nodes.len(), 442);
    assert_eq!(project.elements.len(), 2138);
}
