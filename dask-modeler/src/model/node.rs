//! Node model definitions for structural joints.

use serde::{Deserialize, Serialize};

/// ECS-independent node definition used by persistence and engineering logic.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct NodeData {
    /// Unique node identifier.
    pub id: u32,
    /// X coordinate (engineering units, f64).
    pub x: f64,
    /// Y coordinate (engineering units, f64).
    pub y: f64,
    /// Z coordinate (engineering units, f64).
    pub z: f64,
    /// Floor index.
    pub floor: u32,
    /// Zone name from imported model data.
    pub zone: String,
    /// Restraints [Ux, Uy, Uz, Rx, Ry, Rz].
    pub restraints: [bool; 6],
}

impl NodeData {
    /// Creates a node with free degrees of freedom by default.
    pub fn new(id: u32, x: f64, y: f64, z: f64, floor: u32, zone: impl Into<String>) -> Self {
        Self {
            id,
            x,
            y,
            z,
            floor,
            zone: zone.into(),
            restraints: [false; 6],
        }
    }

    /// Returns coordinates as an array.
    pub fn coords(&self) -> [f64; 3] {
        [self.x, self.y, self.z]
    }
}

#[cfg(test)]
mod tests {
    use super::NodeData;

    #[test]
    fn node_defaults_to_unrestrained() {
        let node = NodeData::new(1, 0.0, 1.0, 2.0, 0, "podium");
        assert_eq!(node.restraints, [false; 6]);
        assert_eq!(node.coords(), [0.0, 1.0, 2.0]);
    }
}
