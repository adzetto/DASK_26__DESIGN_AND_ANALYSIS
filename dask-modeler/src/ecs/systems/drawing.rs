//! Interactive drawing systems.

use anyhow::Result;
use bevy::prelude::*;
use log::warn;

use crate::commands::{AddElementCommand, AddNodeCommand, DeleteElementsCommand, UndoStack};
use crate::ecs::components::{ElementType, NodeMarker, StructuralNode};
use crate::ecs::resources::{
    DrawingState, ModelChangeState, ModelStats, ProjectResource, SelectionState, SnapSettings,
    ToolMode,
};
use crate::model::{ElementData, NodeData};

const NODE_SNAP_WORLD_SCALE: f32 = 0.05;

#[derive(Clone, Copy, Debug)]
struct SnapTarget {
    position: Vec3,
    node_id: Option<u32>,
}

/// Aligns drawing-state element type with selected tool mode.
pub fn sync_tool_mode_to_drawing_state(
    tool_mode: Res<'_, ToolMode>,
    mut drawing_state: ResMut<'_, DrawingState>,
) {
    let target_type = match *tool_mode {
        ToolMode::DrawBeam => ElementType::BeamX,
        ToolMode::DrawColumn => ElementType::Column,
        ToolMode::DrawBrace => ElementType::BraceXZ,
        _ => return,
    };
    if drawing_state.element_type != target_type {
        drawing_state.element_type = target_type;
    }
}

/// Toggles continuous draw with `Tab`.
pub fn toggle_continuous_draw(
    keys: Res<'_, ButtonInput<KeyCode>>,
    tool_mode: Res<'_, ToolMode>,
    mut drawing_state: ResMut<'_, DrawingState>,
) {
    if is_draw_mode(*tool_mode) && keys.just_pressed(KeyCode::Tab) {
        drawing_state.continuous = !drawing_state.continuous;
    }
}

/// Cancels active drawing chain on Escape.
pub fn cancel_drawing_with_escape(
    keys: Res<'_, ButtonInput<KeyCode>>,
    mut drawing_state: ResMut<'_, DrawingState>,
) {
    if keys.just_pressed(KeyCode::Escape) {
        drawing_state.first_node = None;
        drawing_state.preview_end = None;
    }
}

/// Draws snap crosshair and preview dashed line.
pub fn draw_snap_and_preview(
    mut gizmos: Gizmos<'_, '_>,
    tool_mode: Res<'_, ToolMode>,
    snap: Res<'_, SnapSettings>,
    stats: Res<'_, ModelStats>,
    mut drawing_state: ResMut<'_, DrawingState>,
    node_query: Query<'_, '_, &StructuralNode, With<NodeMarker>>,
) {
    if !is_draw_mode(*tool_mode) {
        drawing_state.preview_end = None;
        return;
    }

    let snap_target = find_snap_target(stats.cursor_world_pos, &snap, &node_query);
    drawing_state.preview_end = Some(snap_target.position);
    draw_crosshair(&mut gizmos, snap_target.position);

    if let Some(first_node_id) = drawing_state.first_node
        && let Some(start) = node_position(first_node_id, &node_query)
    {
        draw_dashed_line(
            &mut gizmos,
            start,
            snap_target.position,
            Color::srgb(1.0, 1.0, 1.0),
            24,
        );
    }
}

/// Handles click-to-draw flow for beam/column/brace.
pub fn handle_drawing_clicks(
    mouse: Res<'_, ButtonInput<MouseButton>>,
    tool_mode: Res<'_, ToolMode>,
    snap: Res<'_, SnapSettings>,
    stats: Res<'_, ModelStats>,
    mut drawing_state: ResMut<'_, DrawingState>,
    node_query: Query<'_, '_, &StructuralNode, With<NodeMarker>>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut model_change: ResMut<'_, ModelChangeState>,
) {
    if !is_draw_mode(*tool_mode) || !mouse.just_pressed(MouseButton::Left) {
        return;
    }

    let target = find_snap_target(stats.cursor_world_pos, &snap, &node_query);
    let target_node = match resolve_or_create_node(target, &mut project_res, &mut undo_stack) {
        Ok(node_id) => node_id,
        Err(err) => {
            warn!("failed to resolve draw target node: {err:#}");
            return;
        }
    };

    if let Some(first_node) = drawing_state.first_node {
        if first_node == target_node {
            return;
        }
        let element_type = element_type_from_tool(*tool_mode, &drawing_state.element_type);
        let element_id = project_res.project.next_element_id;
        let Some(start) = project_res.project.nodes.get(&first_node) else {
            drawing_state.first_node = None;
            return;
        };
        let Some(end) = project_res.project.nodes.get(&target_node) else {
            drawing_state.first_node = None;
            return;
        };
        let length =
            ((end.x - start.x).powi(2) + (end.y - start.y).powi(2) + (end.z - start.z).powi(2))
                .sqrt();

        let element = ElementData::new(element_id, first_node, target_node, element_type, length);
        if let Err(err) = undo_stack.execute(
            Box::new(AddElementCommand::new(element)),
            &mut project_res.project,
        ) {
            warn!("failed to add element: {err:#}");
            return;
        }

        if drawing_state.continuous {
            drawing_state.first_node = Some(target_node);
        } else {
            drawing_state.first_node = None;
        }
        model_change.dirty = true;
    } else {
        drawing_state.first_node = Some(target_node);
    }
}

/// Handles keyboard undo/redo/delete commands.
pub fn handle_edit_shortcuts(
    keys: Res<'_, ButtonInput<KeyCode>>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut model_change: ResMut<'_, ModelChangeState>,
    mut selection_state: ResMut<'_, SelectionState>,
) {
    let ctrl = keys.pressed(KeyCode::ControlLeft) || keys.pressed(KeyCode::ControlRight);
    if ctrl && keys.just_pressed(KeyCode::KeyZ) {
        match undo_stack.undo(&mut project_res.project) {
            Ok(true) => {
                model_change.dirty = true;
                selection_state.selected_elements.clear();
                selection_state.selected_nodes.clear();
            }
            Ok(false) => {}
            Err(err) => warn!("undo failed: {err:#}"),
        }
    }
    if ctrl && keys.just_pressed(KeyCode::KeyY) {
        match undo_stack.redo(&mut project_res.project) {
            Ok(true) => {
                model_change.dirty = true;
                selection_state.selected_elements.clear();
                selection_state.selected_nodes.clear();
            }
            Ok(false) => {}
            Err(err) => warn!("redo failed: {err:#}"),
        }
    }

    if keys.just_pressed(KeyCode::Delete) && !selection_state.selected_elements.is_empty() {
        let cmd = DeleteElementsCommand::new(selection_state.selected_elements.clone());
        if let Err(err) = undo_stack.execute(Box::new(cmd), &mut project_res.project) {
            warn!("delete failed: {err:#}");
            return;
        }
        selection_state.selected_elements.clear();
        selection_state.selected_nodes.clear();
        model_change.dirty = true;
    }
}

/// Applies coordinate-input node for precise drawing.
pub fn apply_coordinate_input_to_drawing(
    position: Vec3,
    tool_mode: ToolMode,
    drawing_state: &mut DrawingState,
    project_res: &mut ProjectResource,
    undo_stack: &mut UndoStack,
    model_change: &mut ModelChangeState,
) {
    if !is_draw_mode(tool_mode) {
        return;
    }

    let target = SnapTarget {
        position,
        node_id: find_existing_node_at(position, &project_res.project),
    };

    let Ok(target_node) = resolve_or_create_node(target, project_res, undo_stack) else {
        return;
    };

    if let Some(first_node) = drawing_state.first_node {
        if first_node == target_node {
            return;
        }
        let element_type = element_type_from_tool(tool_mode, &drawing_state.element_type);
        let element_id = project_res.project.next_element_id;
        let Some(start) = project_res.project.nodes.get(&first_node) else {
            drawing_state.first_node = None;
            return;
        };
        let Some(end) = project_res.project.nodes.get(&target_node) else {
            drawing_state.first_node = None;
            return;
        };
        let length =
            ((end.x - start.x).powi(2) + (end.y - start.y).powi(2) + (end.z - start.z).powi(2))
                .sqrt();
        let element = ElementData::new(element_id, first_node, target_node, element_type, length);
        if undo_stack
            .execute(
                Box::new(AddElementCommand::new(element)),
                &mut project_res.project,
            )
            .is_ok()
        {
            drawing_state.first_node = if drawing_state.continuous {
                Some(target_node)
            } else {
                None
            };
            model_change.dirty = true;
        }
    } else {
        drawing_state.first_node = Some(target_node);
    }
}

fn resolve_or_create_node(
    target: SnapTarget,
    project_res: &mut ProjectResource,
    undo_stack: &mut UndoStack,
) -> Result<u32> {
    if let Some(node_id) = target.node_id {
        return Ok(node_id);
    }
    if let Some(existing_id) = find_existing_node_at(target.position, &project_res.project) {
        return Ok(existing_id);
    }

    let node_id = project_res.project.next_node_id;
    let floor = ((target.position.z / 6.0).round().max(0.0)) as u32;
    let node = NodeData::new(
        node_id,
        target.position.x as f64,
        target.position.y as f64,
        target.position.z as f64,
        floor,
        "custom",
    );
    undo_stack.execute(
        Box::new(AddNodeCommand::new(node)),
        &mut project_res.project,
    )?;
    Ok(node_id)
}

fn find_existing_node_at(position: Vec3, project: &crate::model::Project) -> Option<u32> {
    project.nodes.values().find_map(|node| {
        let p = Vec3::new(node.x as f32, node.y as f32, node.z as f32);
        if p.distance(position) < 1e-4 {
            Some(node.id)
        } else {
            None
        }
    })
}

fn is_draw_mode(mode: ToolMode) -> bool {
    matches!(
        mode,
        ToolMode::DrawBeam | ToolMode::DrawColumn | ToolMode::DrawBrace
    )
}

fn element_type_from_tool(mode: ToolMode, fallback: &ElementType) -> crate::model::ElementType {
    match mode {
        ToolMode::DrawBeam => crate::model::ElementType::BeamX,
        ToolMode::DrawColumn => crate::model::ElementType::Column,
        ToolMode::DrawBrace => crate::model::ElementType::BraceXZ,
        _ => map_ecs_type(fallback),
    }
}

fn map_ecs_type(element_type: &ElementType) -> crate::model::ElementType {
    match element_type {
        ElementType::BeamX => crate::model::ElementType::BeamX,
        ElementType::BeamY => crate::model::ElementType::BeamY,
        ElementType::Column => crate::model::ElementType::Column,
        ElementType::BraceXZ => crate::model::ElementType::BraceXZ,
        ElementType::BraceYZ => crate::model::ElementType::BraceYZ,
        ElementType::BraceFloor => crate::model::ElementType::BraceFloor,
        ElementType::CoreWall => crate::model::ElementType::CoreWall,
        ElementType::Chevron => crate::model::ElementType::Chevron,
        ElementType::BraceSpace => crate::model::ElementType::BraceSpace,
        ElementType::Custom(name) => crate::model::ElementType::Custom(name.clone()),
    }
}

fn node_position(
    node_id: u32,
    node_query: &Query<'_, '_, &StructuralNode, With<NodeMarker>>,
) -> Option<Vec3> {
    node_query.iter().find(|n| n.id == node_id).map(|n| {
        Vec3::new(
            n.position[0] as f32,
            n.position[1] as f32,
            n.position[2] as f32,
        )
    })
}

fn find_snap_target(
    cursor_world_pos: Vec3,
    snap: &SnapSettings,
    node_query: &Query<'_, '_, &StructuralNode, With<NodeMarker>>,
) -> SnapTarget {
    let node_snap_threshold = snap.snap_distance * NODE_SNAP_WORLD_SCALE;
    if snap.snap_to_node {
        let mut best: Option<(u32, Vec3, f32)> = None;
        for node in node_query.iter() {
            let p = Vec3::new(
                node.position[0] as f32,
                node.position[1] as f32,
                node.position[2] as f32,
            );
            let dist = p.distance(cursor_world_pos);
            if dist <= node_snap_threshold {
                match best {
                    Some((_, _, best_dist)) if dist >= best_dist => {}
                    _ => best = Some((node.id, p, dist)),
                }
            }
        }
        if let Some((node_id, position, _)) = best {
            return SnapTarget {
                position,
                node_id: Some(node_id),
            };
        }
    }

    if snap.snap_to_grid {
        let size = snap.grid_snap_size.max(0.01);
        let snapped = Vec3::new(
            (cursor_world_pos.x / size).round() * size,
            (cursor_world_pos.y / size).round() * size,
            (cursor_world_pos.z / size).round() * size,
        );
        return SnapTarget {
            position: snapped,
            node_id: None,
        };
    }

    SnapTarget {
        position: cursor_world_pos,
        node_id: None,
    }
}

fn draw_crosshair(gizmos: &mut Gizmos<'_, '_>, p: Vec3) {
    let size = 0.25;
    let color = Color::srgb(1.0, 1.0, 1.0);
    gizmos.line(
        Vec3::new(p.x - size, p.y, p.z),
        Vec3::new(p.x + size, p.y, p.z),
        color,
    );
    gizmos.line(
        Vec3::new(p.x, p.y - size, p.z),
        Vec3::new(p.x, p.y + size, p.z),
        color,
    );
    gizmos.line(
        Vec3::new(p.x, p.y, p.z - size),
        Vec3::new(p.x, p.y, p.z + size),
        color,
    );
}

fn draw_dashed_line(
    gizmos: &mut Gizmos<'_, '_>,
    start: Vec3,
    end: Vec3,
    color: Color,
    segments: usize,
) {
    if segments < 2 {
        gizmos.line(start, end, color);
        return;
    }
    let delta = end - start;
    for i in 0..segments {
        if i % 2 != 0 {
            continue;
        }
        let t0 = i as f32 / segments as f32;
        let t1 = (i + 1) as f32 / segments as f32;
        gizmos.line(start + delta * t0, start + delta * t1, color);
    }
}
