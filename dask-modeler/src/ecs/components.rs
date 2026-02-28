//! ECS components for structural entities and editor tags.

use bevy::prelude::*;
use serde::{Deserialize, Serialize};

/// Node zone labels used for grouping/filtering.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum NodeZone {
    Podium,
    Tower,
    ChevronNode,
    Bridge,
    Custom(String),
}

impl NodeZone {
    /// Parses zone token from CSV/model data.
    pub fn from_str(value: &str) -> Self {
        match value {
            "podium" => Self::Podium,
            "tower" => Self::Tower,
            "chevron_node" => Self::ChevronNode,
            "bridge" => Self::Bridge,
            other => Self::Custom(other.to_owned()),
        }
    }
}

/// ECS component representing a structural node.
#[derive(Component, Clone, Debug, Serialize, Deserialize)]
pub struct StructuralNode {
    /// Node id.
    pub id: u32,
    /// Engineering position [x, y, z].
    pub position: [f64; 3],
    /// Floor index.
    pub floor: u32,
    /// Zone classification.
    pub zone: NodeZone,
    /// Restraints [Ux, Uy, Uz, Rx, Ry, Rz].
    pub restraints: [bool; 6],
}

/// ECS element category mirroring imported structural member classes.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
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
    /// CSV token to enum parser.
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

    /// Default element display color.
    pub fn default_color(&self) -> Color {
        match self {
            Self::BeamX => Color::srgb(0.2, 0.6, 1.0),
            Self::BeamY => Color::srgb(0.2, 0.8, 0.6),
            Self::Column => Color::srgb(1.0, 0.3, 0.3),
            Self::BraceXZ => Color::srgb(1.0, 0.8, 0.2),
            Self::BraceYZ => Color::srgb(1.0, 0.5, 0.0),
            Self::BraceFloor => Color::srgb(0.6, 0.4, 0.8),
            Self::CoreWall => Color::srgb(0.5, 0.5, 0.5),
            Self::Chevron => Color::srgb(0.0, 0.8, 0.0),
            Self::BraceSpace => Color::srgb(1.0, 0.0, 1.0),
            Self::Custom(_) => Color::WHITE,
        }
    }
}

impl From<crate::model::element::ElementType> for ElementType {
    fn from(value: crate::model::element::ElementType) -> Self {
        match value {
            crate::model::element::ElementType::BeamX => Self::BeamX,
            crate::model::element::ElementType::BeamY => Self::BeamY,
            crate::model::element::ElementType::Column => Self::Column,
            crate::model::element::ElementType::BraceXZ => Self::BraceXZ,
            crate::model::element::ElementType::BraceYZ => Self::BraceYZ,
            crate::model::element::ElementType::BraceFloor => Self::BraceFloor,
            crate::model::element::ElementType::CoreWall => Self::CoreWall,
            crate::model::element::ElementType::Chevron => Self::Chevron,
            crate::model::element::ElementType::BraceSpace => Self::BraceSpace,
            crate::model::element::ElementType::Custom(s) => Self::Custom(s),
        }
    }
}

/// ECS component representing a structural line element.
#[derive(Component, Clone, Debug, Serialize, Deserialize)]
pub struct StructuralElement {
    /// Element id.
    pub id: u32,
    /// Start node id.
    pub node_i: u32,
    /// End node id.
    pub node_j: u32,
    /// Element category.
    pub element_type: ElementType,
    /// Optional section assignment.
    pub section_id: Option<u32>,
    /// Optional material assignment.
    pub material_id: Option<u32>,
    /// End releases at i-end [Ux, Uy, Uz, Rx, Ry, Rz].
    pub releases_i: [bool; 6],
    /// End releases at j-end [Ux, Uy, Uz, Rx, Ry, Rz].
    pub releases_j: [bool; 6],
}

/// Tag: currently selected entity.
#[derive(Component, Default)]
pub struct Selected;

/// Tag: currently hovered entity.
#[derive(Component, Default)]
pub struct Hovered;

/// Tag: visible entity.
#[derive(Component, Default)]
pub struct Visible;

/// Tag: structural node ECS entity.
#[derive(Component, Default)]
pub struct NodeMarker;

/// Tag: structural element ECS entity.
#[derive(Component, Default)]
pub struct ElementMarker;
