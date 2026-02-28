//! Camera controls, view presets, and projection switching.

use bevy::prelude::*;
use bevy_panorbit_camera::PanOrbitCamera;

use crate::ecs::components::{NodeMarker, StructuralNode};
use crate::ecs::resources::ViewMode;

/// Tag for the primary scene camera.
#[derive(Component, Default)]
pub struct MainCamera;

/// Handles keyboard-driven view presets and projection toggling.
pub fn keyboard_view_presets(
    keys: Res<'_, ButtonInput<KeyCode>>,
    mut view_mode: ResMut<'_, ViewMode>,
    mut camera_query: Query<
        '_,
        '_,
        (&mut Transform, &mut Projection, &mut PanOrbitCamera),
        With<MainCamera>,
    >,
    node_query: Query<'_, '_, &StructuralNode, With<NodeMarker>>,
) {
    let ctrl = keys.pressed(KeyCode::ControlLeft) || keys.pressed(KeyCode::ControlRight);
    if !ctrl {
        if keys.just_pressed(KeyCode::Digit1) {
            *view_mode = ViewMode::Plan;
        }
        if keys.just_pressed(KeyCode::Digit2) {
            *view_mode = ViewMode::Front;
        }
        if keys.just_pressed(KeyCode::Digit3) {
            *view_mode = ViewMode::Side;
        }
        if keys.just_pressed(KeyCode::Digit4) {
            *view_mode = ViewMode::View3D;
        }
    }

    if keys.just_pressed(KeyCode::Digit5)
        && let Ok((_, mut projection, pan_orbit)) = camera_query.single_mut()
    {
        match &*projection {
            Projection::Perspective(_) => {
                let mut ortho = OrthographicProjection::default_3d();
                ortho.scale = pan_orbit.target_radius.max(1.0) / 12.0;
                *projection = Projection::Orthographic(ortho);
            }
            Projection::Orthographic(_) => {
                *projection = Projection::Perspective(PerspectiveProjection::default());
            }
            _ => {}
        }
    }

    if keys.just_pressed(KeyCode::KeyF)
        && let Ok((mut transform, _, mut pan_orbit)) = camera_query.single_mut()
    {
        zoom_to_fit(&mut transform, &mut pan_orbit, &node_query);
    }
}

/// Applies camera transform updates when the view mode changes.
pub fn apply_view_mode(
    view_mode: Res<'_, ViewMode>,
    mut camera_query: Query<'_, '_, (&mut Transform, &mut PanOrbitCamera), With<MainCamera>>,
    node_query: Query<'_, '_, &StructuralNode, With<NodeMarker>>,
) {
    if !view_mode.is_changed() {
        return;
    }

    let Ok((mut transform, mut pan_orbit)) = camera_query.single_mut() else {
        return;
    };

    let center = model_center(&node_query).unwrap_or(Vec3::new(10.0, 8.0, 76.0));

    match *view_mode {
        ViewMode::Plan => set_camera_pose(
            &mut transform,
            &mut pan_orbit,
            center + Vec3::new(0.0, 0.0, 200.0),
            center,
            Vec3::Y,
        ),
        ViewMode::Front => set_camera_pose(
            &mut transform,
            &mut pan_orbit,
            center + Vec3::new(0.0, -220.0, 0.0),
            center,
            Vec3::Z,
        ),
        ViewMode::Side => set_camera_pose(
            &mut transform,
            &mut pan_orbit,
            center + Vec3::new(-220.0, 0.0, 0.0),
            center,
            Vec3::Z,
        ),
        ViewMode::View3D => set_camera_pose(
            &mut transform,
            &mut pan_orbit,
            center + Vec3::new(90.0, 65.0, 110.0),
            center,
            Vec3::Z,
        ),
    }
}

fn set_camera_pose(
    transform: &mut Transform,
    pan_orbit: &mut PanOrbitCamera,
    eye: Vec3,
    focus: Vec3,
    up: Vec3,
) {
    let radius = eye.distance(focus).max(0.1);
    transform.translation = eye;
    transform.look_at(focus, up);
    pan_orbit.target_focus = focus;
    pan_orbit.focus = focus;
    pan_orbit.target_radius = radius;
    pan_orbit.radius = Some(radius);
    pan_orbit.force_update = true;
}

fn model_center(node_query: &Query<'_, '_, &StructuralNode, With<NodeMarker>>) -> Option<Vec3> {
    let mut count = 0_u32;
    let mut acc = Vec3::ZERO;
    for node in node_query.iter() {
        acc += Vec3::new(
            node.position[0] as f32,
            node.position[1] as f32,
            node.position[2] as f32,
        );
        count += 1;
    }
    if count == 0 {
        None
    } else {
        Some(acc / count as f32)
    }
}

fn zoom_to_fit(
    transform: &mut Transform,
    pan_orbit: &mut PanOrbitCamera,
    node_query: &Query<'_, '_, &StructuralNode, With<NodeMarker>>,
) {
    let mut iter = node_query.iter();
    let Some(first) = iter.next() else {
        return;
    };

    let mut min = Vec3::new(
        first.position[0] as f32,
        first.position[1] as f32,
        first.position[2] as f32,
    );
    let mut max = min;

    for node in iter {
        let p = Vec3::new(
            node.position[0] as f32,
            node.position[1] as f32,
            node.position[2] as f32,
        );
        min = min.min(p);
        max = max.max(p);
    }

    let center = (min + max) * 0.5;
    let diagonal = (max - min).length();
    let distance = (diagonal * 1.6).max(40.0);
    let forward = transform.forward();
    let eye = center - forward * distance;
    set_camera_pose(transform, pan_orbit, eye, center, Vec3::Z);
}
