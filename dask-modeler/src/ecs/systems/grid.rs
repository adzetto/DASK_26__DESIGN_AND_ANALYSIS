//! Grid and axis gizmo rendering.

use bevy::prelude::*;

use crate::ecs::resources::DisplaySettings;

/// Draws XY/XZ/YZ reference grids and axis arrows.
pub fn draw_reference_grids(mut gizmos: Gizmos<'_, '_>, display: Res<'_, DisplaySettings>) {
    if !display.show_grid {
        return;
    }

    let spacing = display.grid_spacing.max(0.1);
    let range = 40_i32;
    let gray = Color::srgba(0.35, 0.35, 0.35, 0.6);

    // XY ground grid (z=0)
    for i in -range..=range {
        let v = i as f32 * spacing;
        gizmos.line(
            Vec3::new(v, -range as f32 * spacing, 0.0),
            Vec3::new(v, range as f32 * spacing, 0.0),
            gray,
        );
        gizmos.line(
            Vec3::new(-range as f32 * spacing, v, 0.0),
            Vec3::new(range as f32 * spacing, v, 0.0),
            gray,
        );
    }

    // XZ reference grid (y = 0)
    for i in -range..=range {
        let v = i as f32 * spacing;
        gizmos.line(
            Vec3::new(v, 0.0, -range as f32 * spacing),
            Vec3::new(v, 0.0, range as f32 * spacing),
            Color::srgba(0.25, 0.25, 0.45, 0.4),
        );
        gizmos.line(
            Vec3::new(-range as f32 * spacing, 0.0, v),
            Vec3::new(range as f32 * spacing, 0.0, v),
            Color::srgba(0.25, 0.25, 0.45, 0.4),
        );
    }

    // YZ reference grid (x = 0)
    for i in -range..=range {
        let v = i as f32 * spacing;
        gizmos.line(
            Vec3::new(0.0, v, -range as f32 * spacing),
            Vec3::new(0.0, v, range as f32 * spacing),
            Color::srgba(0.25, 0.45, 0.25, 0.3),
        );
        gizmos.line(
            Vec3::new(0.0, -range as f32 * spacing, v),
            Vec3::new(0.0, range as f32 * spacing, v),
            Color::srgba(0.25, 0.45, 0.25, 0.3),
        );
    }

    if display.show_axes {
        gizmos.arrow(
            Vec3::ZERO,
            Vec3::new(5.0, 0.0, 0.0),
            Color::srgb(1.0, 0.0, 0.0),
        );
        gizmos.arrow(
            Vec3::ZERO,
            Vec3::new(0.0, 5.0, 0.0),
            Color::srgb(0.0, 1.0, 0.0),
        );
        gizmos.arrow(
            Vec3::ZERO,
            Vec3::new(0.0, 0.0, 5.0),
            Color::srgb(0.0, 0.4, 1.0),
        );
    }
}
