//! 2D label overlay projected from 3D world positions.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::components::{ElementMarker, NodeMarker, StructuralElement, StructuralNode};
use crate::ecs::resources::{DisplaySettings, SelectionState};
use crate::ecs::systems::camera::MainCamera;

/// Draws node/element id labels as screen-space overlays.
pub fn labels_overlay_ui(
    mut contexts: EguiContexts<'_, '_>,
    display: Res<'_, DisplaySettings>,
    selection: Res<'_, SelectionState>,
    camera_query: Query<'_, '_, (&Camera, &GlobalTransform), With<MainCamera>>,
    node_query: Query<'_, '_, &StructuralNode, With<NodeMarker>>,
    element_query: Query<'_, '_, &StructuralElement, With<ElementMarker>>,
) {
    if !display.show_labels {
        return;
    }

    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };
    let Ok((camera, camera_tf)) = camera_query.single() else {
        return;
    };

    let layer = egui::LayerId::new(egui::Order::Foreground, egui::Id::new("labels_overlay"));
    let painter = ctx.layer_painter(layer);
    let font = egui::FontId::monospace(11.0);

    let mut node_positions: std::collections::HashMap<u32, Vec3> = std::collections::HashMap::new();
    for node in &node_query {
        node_positions.insert(
            node.id,
            Vec3::new(
                node.position[0] as f32,
                node.position[1] as f32,
                node.position[2] as f32,
            ),
        );
    }

    let selected_element_node_ids: std::collections::HashSet<u32> =
        if selection.selected_elements.is_empty() {
            std::collections::HashSet::new()
        } else {
            element_query
                .iter()
                .filter(|e| selection.selected_elements.contains(&e.id))
                .flat_map(|e| [e.node_i, e.node_j])
                .collect()
        };

    let label_selected_only =
        !selection.selected_elements.is_empty() || !selection.selected_nodes.is_empty();

    for node in &node_query {
        if label_selected_only
            && !selection.selected_nodes.contains(&node.id)
            && !selection.selected_elements.is_empty()
        {
            if !selected_element_node_ids.contains(&node.id) {
                continue;
            }
        }

        if !label_selected_only && node.id % 10 != 0 {
            continue;
        }

        let world = Vec3::new(
            node.position[0] as f32,
            node.position[1] as f32,
            node.position[2] as f32,
        );
        let Ok(screen) = camera.world_to_viewport(camera_tf, world) else {
            continue;
        };
        painter.text(
            egui::pos2(screen.x + 3.0, screen.y - 3.0),
            egui::Align2::LEFT_BOTTOM,
            format!("N{}", node.id),
            font.clone(),
            egui::Color32::WHITE,
        );
    }

    for element in &element_query {
        if label_selected_only && !selection.selected_elements.contains(&element.id) {
            continue;
        }
        if !label_selected_only && element.id % 8 != 0 {
            continue;
        }

        let Some(p_i) = node_positions.get(&element.node_i).copied() else {
            continue;
        };
        let Some(p_j) = node_positions.get(&element.node_j).copied() else {
            continue;
        };
        let world = (p_i + p_j) * 0.5;
        let Ok(screen) = camera.world_to_viewport(camera_tf, world) else {
            continue;
        };
        painter.text(
            egui::pos2(screen.x + 2.0, screen.y + 2.0),
            egui::Align2::LEFT_TOP,
            format!("E{}", element.id),
            font.clone(),
            egui::Color32::YELLOW,
        );
    }
}
