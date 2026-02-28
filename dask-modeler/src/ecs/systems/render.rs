//! Rendering systems for structural wireframe and node display.

use std::collections::HashMap;

use bevy::prelude::*;

use crate::ecs::components::{
    ElementMarker, ElementType, NodeMarker, Selected, StructuralElement, StructuralNode,
};
use crate::ecs::resources::{ColorMode, DisplaySettings, VisibilityFilter};
use crate::ecs::systems::camera::MainCamera;

/// Updates node mesh visibility/scale to provide batched GPU rendering with camera LOD.
pub fn sync_node_visuals(
    display: Res<'_, DisplaySettings>,
    camera_query: Query<'_, '_, &GlobalTransform, With<MainCamera>>,
    mut node_query: Query<
        '_,
        '_,
        (&StructuralNode, &mut Transform, &mut Visibility),
        With<NodeMarker>,
    >,
) {
    let camera_pos = camera_query.single().ok().map(|t| t.translation());
    let scale = Vec3::splat(display.node_size.max(0.02));

    for (node, mut transform, mut visibility) in &mut node_query {
        transform.scale = scale;
        let point = Vec3::new(
            node.position[0] as f32,
            node.position[1] as f32,
            node.position[2] as f32,
        );
        let visible =
            display.show_nodes && !lod_reject(camera_pos, point, node.id, display.lod_distance, 2);
        *visibility = if visible {
            Visibility::Visible
        } else {
            Visibility::Hidden
        };
    }
}

/// Draws structural elements and optional node markers using Bevy gizmos.
pub fn draw_structural_model(
    mut gizmos: Gizmos<'_, '_>,
    display: Res<'_, DisplaySettings>,
    filter: Res<'_, VisibilityFilter>,
    node_query: Query<'_, '_, &StructuralNode, With<NodeMarker>>,
    element_query: Query<'_, '_, (&StructuralElement, Option<&Selected>), With<ElementMarker>>,
    camera_query: Query<'_, '_, &GlobalTransform, With<MainCamera>>,
) {
    let node_positions: HashMap<u32, (Vec3, u32, [bool; 6])> = node_query
        .iter()
        .map(|n| {
            (
                n.id,
                (
                    Vec3::new(
                        n.position[0] as f32,
                        n.position[1] as f32,
                        n.position[2] as f32,
                    ),
                    n.floor,
                    n.restraints,
                ),
            )
        })
        .collect();

    let camera_pos = camera_query.single().ok().map(|t| t.translation());

    for (element, selected) in &element_query {
        if !element_passes_filter(element, &node_positions, &filter) {
            continue;
        }

        let Some((a, _, _)) = node_positions.get(&element.node_i) else {
            continue;
        };
        let Some((b, _, _)) = node_positions.get(&element.node_j) else {
            continue;
        };
        let midpoint = (*a + *b) * 0.5;

        if lod_reject(camera_pos, midpoint, element.id, display.lod_distance, 3) {
            continue;
        }

        let color = if selected.is_some() {
            Color::srgb(1.0, 1.0, 0.0)
        } else {
            element_color(element, display.color_mode, &node_positions)
        };

        gizmos.line(*a, *b, color);
    }

    if display.show_restraints {
        for (node_id, (position, _, restraints)) in &node_positions {
            if !restraints.iter().any(|v| *v) {
                continue;
            }
            if lod_reject(camera_pos, *position, *node_id, display.lod_distance, 2) {
                continue;
            }
            draw_restraint_marker(&mut gizmos, *position, display.node_size);
        }
    }
}

fn element_passes_filter(
    element: &StructuralElement,
    node_positions: &HashMap<u32, (Vec3, u32, [bool; 6])>,
    filter: &VisibilityFilter,
) -> bool {
    if let Some(expected_type) = &filter.element_type
        && &element.element_type != expected_type
    {
        return false;
    }

    if let Some(floor) = filter.floor {
        let floor_i = node_positions.get(&element.node_i).map(|(_, f, _)| *f);
        let floor_j = node_positions.get(&element.node_j).map(|(_, f, _)| *f);
        return floor_i == Some(floor) || floor_j == Some(floor);
    }

    true
}

fn element_color(
    element: &StructuralElement,
    color_mode: ColorMode,
    node_positions: &HashMap<u32, (Vec3, u32, [bool; 6])>,
) -> Color {
    match color_mode {
        ColorMode::ByElementType => element.element_type.default_color(),
        ColorMode::ByFloor => {
            let floor_i = node_positions
                .get(&element.node_i)
                .map(|(_, f, _)| *f as f32)
                .unwrap_or(0.0);
            let floor_j = node_positions
                .get(&element.node_j)
                .map(|(_, f, _)| *f as f32)
                .unwrap_or(0.0);
            let t = ((floor_i + floor_j) * 0.5 / 30.0).clamp(0.0, 1.0);
            Color::srgb(0.1 + 0.8 * t, 0.9 - 0.6 * t, 0.9)
        }
        ColorMode::BySection => color_from_id(element.section_id.unwrap_or(0)),
        ColorMode::ByMaterial => color_from_id(element.material_id.unwrap_or(0)),
        ColorMode::Uniform => Color::srgb(0.8, 0.8, 0.8),
    }
}

fn color_from_id(id: u32) -> Color {
    if id == 0 {
        return Color::srgb(0.45, 0.45, 0.45);
    }
    let r = ((id.wrapping_mul(97) % 255) as f32 / 255.0).clamp(0.15, 0.95);
    let g = ((id.wrapping_mul(57) % 255) as f32 / 255.0).clamp(0.15, 0.95);
    let b = ((id.wrapping_mul(17) % 255) as f32 / 255.0).clamp(0.15, 0.95);
    Color::srgb(r, g, b)
}

fn draw_restraint_marker(gizmos: &mut Gizmos<'_, '_>, center: Vec3, node_size: f32) {
    let h = node_size * 3.0;
    let p0 = center + Vec3::new(-node_size, -node_size, -h);
    let p1 = center + Vec3::new(node_size, -node_size, -h);
    let p2 = center + Vec3::new(0.0, node_size, -h);
    let c = Color::srgb(1.0, 0.6, 0.1);
    gizmos.line(p0, p1, c);
    gizmos.line(p1, p2, c);
    gizmos.line(p2, p0, c);
}

fn lod_reject(
    camera_pos: Option<Vec3>,
    point: Vec3,
    seed: u32,
    lod_distance: f32,
    keep_every: u32,
) -> bool {
    if let Some(cam) = camera_pos
        && cam.distance(point) > lod_distance
    {
        return keep_every > 1 && !seed.is_multiple_of(keep_every);
    }
    false
}

/// Converts model-independent element type names to ECS element type.
pub fn element_type_from_token(token: &str) -> ElementType {
    ElementType::from_str(token)
}
