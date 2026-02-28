//! Input utility systems.

use bevy::prelude::*;
use bevy::window::PrimaryWindow;

use crate::ecs::resources::ModelStats;
use crate::ecs::systems::camera::MainCamera;

/// Updates cursor world position (intersection with z=0 plane) for the status bar.
pub fn update_cursor_world_position(
    window_query: Query<'_, '_, &Window, With<PrimaryWindow>>,
    camera_query: Query<'_, '_, (&Camera, &GlobalTransform), With<MainCamera>>,
    mut stats: ResMut<'_, ModelStats>,
) {
    let Ok(window) = window_query.single() else {
        return;
    };
    let Some(cursor) = window.cursor_position() else {
        return;
    };
    let Ok((camera, camera_transform)) = camera_query.single() else {
        return;
    };
    let Ok(ray) = camera.viewport_to_world(camera_transform, cursor) else {
        return;
    };

    let dir_z = ray.direction.z;
    if dir_z.abs() < f32::EPSILON {
        return;
    }
    let t = -ray.origin.z / dir_z;
    if t < 0.0 {
        return;
    }
    stats.cursor_world_pos = ray.origin + *ray.direction * t;
}
