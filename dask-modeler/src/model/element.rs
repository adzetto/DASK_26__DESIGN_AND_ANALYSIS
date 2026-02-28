//! Element model definitions for line members.

use serde::{Deserialize, Serialize};

/// Structural line element categories.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq, Hash, Default)]
pub enum ElementType {
    #[default]
    BeamX,
    BeamY,
    Column,
    BraceXZ,
    BraceYZ,
    BraceFloor,
    CoreWall,
    Chevron,
    BraceSpace,
    Custom(String),
}

impl ElementType {
    /// Parses an element type from CSV tokens.
    pub fn from_str(value: &str) -> Self {
        match value {
            "beam_x" => Self::BeamX,
            "beam_y" => Self::BeamY,
            "column" => Self::Column,
            "brace_xz" => Self::BraceXZ,
            "brace_yz" => Self::BraceYZ,
            "brace_floor" => Self::BraceFloor,
            "core_wall" => Self::CoreWall,
            "chevron" => Self::Chevron,
            "brace_space" => Self::BraceSpace,
            other => Self::Custom(other.to_owned()),
        }
    }

    /// Returns the canonical token used by CSV and export serializers.
    pub fn as_str(&self) -> &str {
        match self {
            Self::BeamX => "beam_x",
            Self::BeamY => "beam_y",
            Self::Column => "column",
            Self::BraceXZ => "brace_xz",
            Self::BraceYZ => "brace_yz",
            Self::BraceFloor => "brace_floor",
            Self::CoreWall => "core_wall",
            Self::Chevron => "chevron",
            Self::BraceSpace => "brace_space",
            Self::Custom(value) => value.as_str(),
        }
    }

    /// Returns default display color as normalized RGBA.
    pub fn default_color(&self) -> [f32; 4] {
        match self {
            Self::BeamX => [0.2, 0.6, 1.0, 1.0],
            Self::BeamY => [0.2, 0.8, 0.6, 1.0],
            Self::Column => [1.0, 0.3, 0.3, 1.0],
            Self::BraceXZ => [1.0, 0.8, 0.2, 1.0],
            Self::BraceYZ => [1.0, 0.5, 0.0, 1.0],
            Self::BraceFloor => [0.6, 0.4, 0.8, 1.0],
            Self::CoreWall => [0.5, 0.5, 0.5, 1.0],
            Self::Chevron => [0.0, 0.8, 0.0, 1.0],
            Self::BraceSpace => [1.0, 0.0, 1.0, 1.0],
            Self::Custom(_) => [1.0, 1.0, 1.0, 1.0],
        }
    }
}

/// ECS-independent structural element.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct ElementData {
    /// Unique element identifier.
    pub id: u32,
    /// Start node ID.
    pub node_i: u32,
    /// End node ID.
    pub node_j: u32,
    /// Element category.
    pub element_type: ElementType,
    /// Element length (engineering units).
    pub length: f64,
    /// Optional section assignment.
    pub section_id: Option<u32>,
    /// Optional material assignment.
    pub material_id: Option<u32>,
    /// End releases at i-end [Ux, Uy, Uz, Rx, Ry, Rz].
    pub releases_i: [bool; 6],
    /// End releases at j-end [Ux, Uy, Uz, Rx, Ry, Rz].
    pub releases_j: [bool; 6],
}

impl ElementData {
    /// Creates a line element with default unreleased ends.
    pub fn new(id: u32, node_i: u32, node_j: u32, element_type: ElementType, length: f64) -> Self {
        Self {
            id,
            node_i,
            node_j,
            element_type,
            length,
            section_id: None,
            material_id: None,
            releases_i: [false; 6],
            releases_j: [false; 6],
        }
    }
}

#[cfg(test)]
mod tests {
    use super::ElementType;

    #[test]
    fn parser_maps_known_values() {
        assert_eq!(ElementType::from_str("beam_x"), ElementType::BeamX);
        assert_eq!(
            ElementType::from_str("brace_space"),
            ElementType::BraceSpace
        );
    }

    #[test]
    fn parser_preserves_unknown_values() {
        assert_eq!(
            ElementType::from_str("custom_member"),
            ElementType::Custom("custom_member".to_string())
        );
    }
}
