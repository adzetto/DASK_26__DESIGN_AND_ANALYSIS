//! Transform, marquee-selection, and selection-filter systems.

use std::collections::HashSet;

use bevy::prelude::*;
use bevy::window::PrimaryWindow;
use log::warn;

use crate::commands::{CopyElementsCommand, MirrorElementsCommand, MoveNodesCommand, UndoStack};
use crate::ecs::components::{ElementMarker, Selected, StructuralElement};
use crate::ecs::events::SelectionChangedEvent;
use crate::ecs::resources::{
    ModelChangeState, ModelStats, ProjectResource, SelectionState, SelectionTypeFilter, ToolMode,
    TransformOpsState,
};
use crate::ecs::systems::camera::MainCamera;

/// Handles keyboard shortcuts that open transform dialogs.
pub fn handle_transform_shortcuts(
    keys: Res<'_, ButtonInput<KeyCode>>,
    mut ops: ResMut<'_, TransformOpsState>,
) {
    let ctrl = keys.pressed(KeyCode::ControlLeft) || keys.pressed(KeyCode::ControlRight);
    let shift = keys.pressed(KeyCode::ShiftLeft) || keys.pressed(KeyCode::ShiftRight);

    if keys.just_pressed(KeyCode::KeyM) {
        ops.move_open = true;
    }
    if ctrl && keys.just_pressed(KeyCode::KeyD) {
        if shift {
            ops.array_open = true;
        } else {
            ops.copy_open = true;
        }
    }
    if ctrl && keys.just_pressed(KeyCode::KeyR) {
        ops.mirror_open = true;
    }
}

/// Applies move/copy/array/mirror requests produced by UI panels.
pub fn apply_transform_requests(
    mut ops: ResMut<'_, TransformOpsState>,
    selection: Res<'_, SelectionState>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut model_change: ResMut<'_, ModelChangeState>,
) {
    if ops.move_apply_requested {
        ops.move_apply_requested = false;
        let node_ids = selected_node_ids(&selection, &project_res.project);
        let delta = [ops.move_dx, ops.move_dy, ops.move_dz];
        apply_move(
            &node_ids,
            delta,
            &mut undo_stack,
            &mut project_res,
            &mut model_change,
        );
    }

    if ops.copy_apply_requested {
        ops.copy_apply_requested = false;
        let element_ids = selected_element_ids(&selection, &project_res.project);
        let offset = [ops.copy_dx, ops.copy_dy, ops.copy_dz];
        apply_copy(
            &element_ids,
            offset,
            1,
            &mut undo_stack,
            &mut project_res,
            &mut model_change,
        );
    }

    if ops.array_apply_requested {
        ops.array_apply_requested = false;
        let element_ids = selected_element_ids(&selection, &project_res.project);
        let offset = [ops.array_dx, ops.array_dy, ops.array_dz];
        let repeats = ops.array_count.max(1);
        apply_copy(
            &element_ids,
            offset,
            repeats,
            &mut undo_stack,
            &mut project_res,
            &mut model_change,
        );
    }

    if ops.mirror_apply_requested {
        ops.mirror_apply_requested = false;
        let element_ids = selected_element_ids(&selection, &project_res.project);
        apply_mirror(
            &element_ids,
            ops.mirror_plane,
            ops.mirror_position,
            &mut undo_stack,
            &mut project_res,
            &mut model_change,
        );
    }
}

/// Handles drag-move when Move tool is active.
pub fn handle_node_drag_move(
    tool_mode: Res<'_, ToolMode>,
    mouse: Res<'_, ButtonInput<MouseButton>>,
    stats: Res<'_, ModelStats>,
    selection: Res<'_, SelectionState>,
    mut ops: ResMut<'_, TransformOpsState>,
    mut undo_stack: ResMut<'_, UndoStack>,
    mut project_res: ResMut<'_, ProjectResource>,
    mut model_change: ResMut<'_, ModelChangeState>,
) {
    if *tool_mode != ToolMode::MoveNode {
        ops.drag_move_active = false;
        ops.drag_origin = None;
        return;
    }

    if mouse.just_pressed(MouseButton::Left) {
        let node_ids = selected_node_ids(&selection, &project_res.project);
        if node_ids.is_empty() {
            return;
        }
        ops.drag_move_active = true;
        ops.drag_origin = Some(stats.cursor_world_pos);
    }

    if !ops.drag_move_active {
        return;
    }

    if let Some(origin) = ops.drag_origin {
        let delta = stats.cursor_world_pos - origin;
        ops.move_dx = delta.x as f64;
        ops.move_dy = delta.y as f64;
        ops.move_dz = delta.z as f64;
    }

    if mouse.just_released(MouseButton::Left) {
        let Some(origin) = ops.drag_origin else {
            ops.drag_move_active = false;
            return;
        };
        let delta = stats.cursor_world_pos - origin;
        let move_delta = [delta.x as f64, delta.y as f64, delta.z as f64];
        let node_ids = selected_node_ids(&selection, &project_res.project);
        apply_move(
            &node_ids,
            move_delta,
            &mut undo_stack,
            &mut project_res,
            &mut model_change,
        );
        ops.drag_move_active = false;
        ops.drag_origin = None;
        ops.move_dx = 0.0;
        ops.move_dy = 0.0;
        ops.move_dz = 0.0;
    }
}

/// Handles window selection (left-to-right inside, right-to-left crossing).
pub fn handle_window_selection(
    mut commands: Commands<'_, '_>,
    mouse: Res<'_, ButtonInput<MouseButton>>,
    keys: Res<'_, ButtonInput<KeyCode>>,
    tool_mode: Res<'_, ToolMode>,
    window_query: Query<'_, '_, &Window, With<PrimaryWindow>>,
    camera_query: Query<'_, '_, (&Camera, &GlobalTransform), With<MainCamera>>,
    project_res: Res<'_, ProjectResource>,
    type_filter: Res<'_, SelectionTypeFilter>,
    mut selection_state: ResMut<'_, SelectionState>,
    mut model_stats: ResMut<'_, ModelStats>,
    mut changed: MessageWriter<'_, SelectionChangedEvent>,
    element_query: Query<'_, '_, (Entity, &StructuralElement), With<ElementMarker>>,
    selected_query: Query<'_, '_, Entity, (With<ElementMarker>, With<Selected>)>,
) {
    if *tool_mode != ToolMode::Select {
        selection_state.box_select_start = None;
        selection_state.box_select_end = None;
        return;
    }

    let Ok(window) = window_query.single() else {
        return;
    };

    if mouse.just_pressed(MouseButton::Left) {
        if let Some(cursor) = window.cursor_position() {
            selection_state.box_select_start = Some(cursor);
            selection_state.box_select_end = Some(cursor);
        }
        return;
    }

    if mouse.pressed(MouseButton::Left)
        && let Some(cursor) = window.cursor_position()
        && selection_state.box_select_start.is_some()
    {
        selection_state.box_select_end = Some(cursor);
        return;
    }

    if !mouse.just_released(MouseButton::Left) {
        return;
    }

    let Some(start) = selection_state.box_select_start.take() else {
        return;
    };
    let end = selection_state.box_select_end.take().unwrap_or(start);

    if (end - start).length() < 6.0 {
        return;
    }

    let add_mode = keys.pressed(KeyCode::ShiftLeft) || keys.pressed(KeyCode::ShiftRight);
    let toggle_mode = keys.pressed(KeyCode::ControlLeft) || keys.pressed(KeyCode::ControlRight);
    let left_to_right = end.x >= start.x;
    let rect = rect_from_points(start, end);

    let Ok((camera, camera_transform)) = camera_query.single() else {
        return;
    };

    let mut matches: Vec<(Entity, u32)> = Vec::new();
    for (entity, element) in &element_query {
        if !type_filter.allows(&element.element_type) {
            continue;
        }
        if element_hits_marquee(
            element,
            rect,
            left_to_right,
            camera,
            camera_transform,
            &project_res.project,
        ) {
            matches.push((entity, element.id));
        }
    }

    let mut changed_any = false;
    if !add_mode && !toggle_mode {
        for selected_entity in &selected_query {
            commands.entity(selected_entity).remove::<Selected>();
        }
        if !selection_state.selected_elements.is_empty() {
            changed_any = true;
        }
        selection_state.selected_elements.clear();
    }

    if toggle_mode {
        for (entity, element_id) in matches {
            if selection_state.selected_elements.contains(&element_id) {
                commands.entity(entity).remove::<Selected>();
                selection_state
                    .selected_elements
                    .retain(|id| *id != element_id);
            } else {
                commands.entity(entity).insert(Selected);
                selection_state.selected_elements.push(element_id);
            }
            changed_any = true;
        }
    } else {
        for (entity, element_id) in matches {
            if !selection_state.selected_elements.contains(&element_id) {
                commands.entity(entity).insert(Selected);
                selection_state.selected_elements.push(element_id);
                changed_any = true;
            }
        }
    }

    if changed_any {
        selection_state.selected_nodes.clear();
        model_stats.selected_count = selection_state.selected_elements.len();
        changed.write(SelectionChangedEvent);
    }
}

/// Draws previews for active transform dialogs and drag move.
pub fn draw_transform_previews(
    mut gizmos: Gizmos<'_, '_>,
    ops: Res<'_, TransformOpsState>,
    selection: Res<'_, SelectionState>,
    project_res: Res<'_, ProjectResource>,
) {
    let project = &project_res.project;
    if project.nodes.is_empty() || project.elements.is_empty() {
        return;
    }

    if ops.move_open || ops.drag_move_active {
        let node_ids = selected_node_ids(&selection, project);
        let delta = Vec3::new(ops.move_dx as f32, ops.move_dy as f32, ops.move_dz as f32);
        if delta.length_squared() > 0.0 {
            for node_id in node_ids {
                let Some(node) = project.nodes.get(&node_id) else {
                    continue;
                };
                let p = Vec3::new(node.x as f32, node.y as f32, node.z as f32);
                gizmos.line(p, p + delta, Color::srgb(0.1, 1.0, 1.0));
            }
        }
    }

    if ops.copy_open {
        draw_translated_element_preview(
            &mut gizmos,
            project,
            &selection.selected_elements,
            Vec3::new(ops.copy_dx as f32, ops.copy_dy as f32, ops.copy_dz as f32),
            Color::srgb(0.1, 1.0, 1.0),
        );
    }

    if ops.array_open {
        let max_repeats = ops.array_count.min(24);
        let base = Vec3::new(
            ops.array_dx as f32,
            ops.array_dy as f32,
            ops.array_dz as f32,
        );
        for i in 1..=max_repeats {
            let delta = base * i as f32;
            draw_translated_element_preview(
                &mut gizmos,
                project,
                &selection.selected_elements,
                delta,
                Color::srgb(0.2, 0.8, 1.0),
            );
        }
    }

    if ops.mirror_open {
        draw_mirror_element_preview(
            &mut gizmos,
            project,
            &selection.selected_elements,
            ops.mirror_plane,
            ops.mirror_position,
            Color::srgb(1.0, 0.8, 0.3),
        );
    }
}

fn apply_move(
    node_ids: &[u32],
    delta: [f64; 3],
    undo_stack: &mut UndoStack,
    project_res: &mut ProjectResource,
    model_change: &mut ModelChangeState,
) {
    if node_ids.is_empty() {
        return;
    }
    if delta.iter().all(|v| v.abs() < f64::EPSILON) {
        return;
    }

    let command = MoveNodesCommand::new(node_ids.to_vec(), delta);
    match undo_stack.execute(Box::new(command), &mut project_res.project) {
        Ok(()) => model_change.dirty = true,
        Err(err) => warn!("move nodes failed: {err:#}"),
    }
}

fn apply_copy(
    element_ids: &[u32],
    offset: [f64; 3],
    repeats: u32,
    undo_stack: &mut UndoStack,
    project_res: &mut ProjectResource,
    model_change: &mut ModelChangeState,
) {
    if element_ids.is_empty() || repeats == 0 {
        return;
    }
    if offset.iter().all(|v| v.abs() < f64::EPSILON) {
        return;
    }

    let command = CopyElementsCommand::new(element_ids.to_vec(), offset, repeats);
    match undo_stack.execute(Box::new(command), &mut project_res.project) {
        Ok(()) => model_change.dirty = true,
        Err(err) => warn!("copy elements failed: {err:#}"),
    }
}

fn apply_mirror(
    element_ids: &[u32],
    plane: crate::commands::MirrorPlane,
    position: f64,
    undo_stack: &mut UndoStack,
    project_res: &mut ProjectResource,
    model_change: &mut ModelChangeState,
) {
    if element_ids.is_empty() {
        return;
    }

    let command = MirrorElementsCommand::new(element_ids.to_vec(), plane, position);
    match undo_stack.execute(Box::new(command), &mut project_res.project) {
        Ok(()) => model_change.dirty = true,
        Err(err) => warn!("mirror elements failed: {err:#}"),
    }
}

fn selected_element_ids(selection: &SelectionState, project: &crate::model::Project) -> Vec<u32> {
    let mut ids: Vec<u32> = selection
        .selected_elements
        .iter()
        .copied()
        .filter(|id| project.elements.contains_key(id))
        .collect();
    ids.sort_unstable();
    ids.dedup();
    ids
}

fn selected_node_ids(selection: &SelectionState, project: &crate::model::Project) -> Vec<u32> {
    let mut ids: Vec<u32> = selection
        .selected_nodes
        .iter()
        .copied()
        .filter(|id| project.nodes.contains_key(id))
        .collect();

    if ids.is_empty() {
        let mut set: HashSet<u32> = HashSet::new();
        for element_id in &selection.selected_elements {
            let Some(element) = project.elements.get(element_id) else {
                continue;
            };
            set.insert(element.node_i);
            set.insert(element.node_j);
        }
        ids.extend(set);
    }

    ids.sort_unstable();
    ids
}

fn draw_translated_element_preview(
    gizmos: &mut Gizmos<'_, '_>,
    project: &crate::model::Project,
    element_ids: &[u32],
    delta: Vec3,
    color: Color,
) {
    if delta.length_squared() == 0.0 {
        return;
    }

    for element_id in element_ids {
        let Some(element) = project.elements.get(element_id) else {
            continue;
        };
        let Some(node_i) = project.nodes.get(&element.node_i) else {
            continue;
        };
        let Some(node_j) = project.nodes.get(&element.node_j) else {
            continue;
        };

        let p0 = Vec3::new(node_i.x as f32, node_i.y as f32, node_i.z as f32) + delta;
        let p1 = Vec3::new(node_j.x as f32, node_j.y as f32, node_j.z as f32) + delta;
        gizmos.line(p0, p1, color);
    }
}

fn draw_mirror_element_preview(
    gizmos: &mut Gizmos<'_, '_>,
    project: &crate::model::Project,
    element_ids: &[u32],
    plane: crate::commands::MirrorPlane,
    plane_position: f64,
    color: Color,
) {
    for element_id in element_ids {
        let Some(element) = project.elements.get(element_id) else {
            continue;
        };
        let Some(node_i) = project.nodes.get(&element.node_i) else {
            continue;
        };
        let Some(node_j) = project.nodes.get(&element.node_j) else {
            continue;
        };

        let mi = mirror_position(
            Vec3::new(node_i.x as f32, node_i.y as f32, node_i.z as f32),
            plane,
            plane_position as f32,
        );
        let mj = mirror_position(
            Vec3::new(node_j.x as f32, node_j.y as f32, node_j.z as f32),
            plane,
            plane_position as f32,
        );
        gizmos.line(mi, mj, color);
    }
}

fn mirror_position(position: Vec3, plane: crate::commands::MirrorPlane, value: f32) -> Vec3 {
    match plane {
        crate::commands::MirrorPlane::XY => {
            Vec3::new(position.x, position.y, 2.0 * value - position.z)
        }
        crate::commands::MirrorPlane::XZ => {
            Vec3::new(position.x, 2.0 * value - position.y, position.z)
        }
        crate::commands::MirrorPlane::YZ => {
            Vec3::new(2.0 * value - position.x, position.y, position.z)
        }
    }
}

fn element_hits_marquee(
    element: &StructuralElement,
    rect: Rect,
    inside_mode: bool,
    camera: &Camera,
    camera_transform: &GlobalTransform,
    project: &crate::model::Project,
) -> bool {
    let Some(node_i) = project.nodes.get(&element.node_i) else {
        return false;
    };
    let Some(node_j) = project.nodes.get(&element.node_j) else {
        return false;
    };

    let world_i = Vec3::new(node_i.x as f32, node_i.y as f32, node_i.z as f32);
    let world_j = Vec3::new(node_j.x as f32, node_j.y as f32, node_j.z as f32);
    let Ok(screen_i) = camera.world_to_viewport(camera_transform, world_i) else {
        return false;
    };
    let Ok(screen_j) = camera.world_to_viewport(camera_transform, world_j) else {
        return false;
    };

    if inside_mode {
        return rect.contains(screen_i) && rect.contains(screen_j);
    }

    if rect.contains(screen_i) || rect.contains(screen_j) {
        return true;
    }

    segment_intersects_rect(screen_i, screen_j, rect)
}

fn rect_from_points(a: Vec2, b: Vec2) -> Rect {
    Rect::from_corners(
        Vec2::new(a.x.min(b.x), a.y.min(b.y)),
        Vec2::new(a.x.max(b.x), a.y.max(b.y)),
    )
}

fn segment_intersects_rect(a: Vec2, b: Vec2, rect: Rect) -> bool {
    let corners = [
        rect.min,
        Vec2::new(rect.max.x, rect.min.y),
        rect.max,
        Vec2::new(rect.min.x, rect.max.y),
    ];
    segments_intersect(a, b, corners[0], corners[1])
        || segments_intersect(a, b, corners[1], corners[2])
        || segments_intersect(a, b, corners[2], corners[3])
        || segments_intersect(a, b, corners[3], corners[0])
}

fn segments_intersect(p1: Vec2, q1: Vec2, p2: Vec2, q2: Vec2) -> bool {
    let o1 = orientation(p1, q1, p2);
    let o2 = orientation(p1, q1, q2);
    let o3 = orientation(p2, q2, p1);
    let o4 = orientation(p2, q2, q1);

    if o1 != o2 && o3 != o4 {
        return true;
    }

    (o1 == 0 && on_segment(p1, p2, q1))
        || (o2 == 0 && on_segment(p1, q2, q1))
        || (o3 == 0 && on_segment(p2, p1, q2))
        || (o4 == 0 && on_segment(p2, q1, q2))
}

fn orientation(p: Vec2, q: Vec2, r: Vec2) -> i32 {
    let value = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y);
    if value.abs() < 1e-6 {
        0
    } else if value > 0.0 {
        1
    } else {
        2
    }
}

fn on_segment(p: Vec2, q: Vec2, r: Vec2) -> bool {
    q.x <= p.x.max(r.x) && q.x >= p.x.min(r.x) && q.y <= p.y.max(r.y) && q.y >= p.y.min(r.y)
}
