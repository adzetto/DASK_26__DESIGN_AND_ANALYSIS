//! Section-cut material, clipping helpers, and plane visualization systems.

use std::f64::EPSILON;

use bevy::pbr::Material;
use bevy::prelude::*;
use bevy::reflect::TypePath;
use bevy::render::render_resource::{AsBindGroup, ShaderType};
use bevy::shader::ShaderRef;
use nalgebra::{Point3, Vector3};

use crate::ecs::components::{ElementMarker, StructuralElement};
use crate::ecs::resources::SectionPlanes;
use crate::model::Project;

const SECTION_CUT_SHADER: &str = "shaders/section_cut.wgsl";

/// Clipping-capable material used for structural elements.
#[derive(Asset, TypePath, AsBindGroup, Debug, Clone)]
pub struct SectionCutMaterial {
    /// Packed uniforms consumed by `assets/shaders/section_cut.wgsl`.
    #[uniform(0)]
    pub params: SectionCutUniforms,
    /// Blend mode.
    pub alpha_mode: AlphaMode,
}

/// GPU uniform pack for clip-plane controls and base color.
#[derive(Clone, Debug, ShaderType)]
pub struct SectionCutUniforms {
    pub base_color: Vec4,
    pub plane_xy: Vec4,
    pub plane_xz: Vec4,
    pub plane_yz: Vec4,
    pub flags: Vec4,
}

impl Default for SectionCutMaterial {
    fn default() -> Self {
        Self {
            params: SectionCutUniforms {
                base_color: Vec4::new(0.8, 0.8, 0.8, 0.35),
                plane_xy: Vec4::new(0.0, 0.0, 1.0, 0.0),
                plane_xz: Vec4::new(0.0, 1.0, 0.0, 0.0),
                plane_yz: Vec4::new(1.0, 0.0, 0.0, 0.0),
                flags: Vec4::new(0.0, 0.0, 0.0, 1.0),
            },
            alpha_mode: AlphaMode::Blend,
        }
    }
}

impl Material for SectionCutMaterial {
    fn fragment_shader() -> ShaderRef {
        SECTION_CUT_SHADER.into()
    }

    fn alpha_mode(&self) -> AlphaMode {
        self.alpha_mode
    }
}

/// Visual kind of section plane.
#[derive(Component, Clone, Copy, Debug, PartialEq, Eq)]
pub enum SectionPlaneVisualKind {
    XY,
    XZ,
    YZ,
}

/// Tag component for semi-transparent plane quads.
#[derive(Component, Clone, Copy, Debug)]
pub struct SectionPlaneVisual {
    pub kind: SectionPlaneVisualKind,
}

/// Spawns translucent quad visuals for XY/XZ/YZ section planes.
pub fn spawn_section_plane_visuals(
    mut commands: Commands<'_, '_>,
    mut meshes: ResMut<'_, Assets<Mesh>>,
    mut materials: ResMut<'_, Assets<StandardMaterial>>,
) {
    let mesh = meshes.add(Plane3d::default().mesh().size(260.0, 260.0));

    let xy_mat = materials.add(StandardMaterial {
        base_color: Color::srgba(0.2, 0.8, 1.0, 0.16),
        alpha_mode: AlphaMode::Blend,
        unlit: true,
        cull_mode: None,
        ..default()
    });
    let xz_mat = materials.add(StandardMaterial {
        base_color: Color::srgba(1.0, 0.7, 0.2, 0.14),
        alpha_mode: AlphaMode::Blend,
        unlit: true,
        cull_mode: None,
        ..default()
    });
    let yz_mat = materials.add(StandardMaterial {
        base_color: Color::srgba(0.3, 1.0, 0.4, 0.14),
        alpha_mode: AlphaMode::Blend,
        unlit: true,
        cull_mode: None,
        ..default()
    });

    commands.spawn((
        Mesh3d(mesh.clone()),
        MeshMaterial3d(xy_mat),
        Transform::from_rotation(Quat::from_rotation_x(std::f32::consts::FRAC_PI_2)),
        Visibility::Hidden,
        SectionPlaneVisual {
            kind: SectionPlaneVisualKind::XY,
        },
        Name::new("Section Plane XY"),
    ));
    commands.spawn((
        Mesh3d(mesh.clone()),
        MeshMaterial3d(xz_mat),
        Transform::IDENTITY,
        Visibility::Hidden,
        SectionPlaneVisual {
            kind: SectionPlaneVisualKind::XZ,
        },
        Name::new("Section Plane XZ"),
    ));
    commands.spawn((
        Mesh3d(mesh),
        MeshMaterial3d(yz_mat),
        Transform::from_rotation(Quat::from_rotation_z(-std::f32::consts::FRAC_PI_2)),
        Visibility::Hidden,
        SectionPlaneVisual {
            kind: SectionPlaneVisualKind::YZ,
        },
        Name::new("Section Plane YZ"),
    ));
}

/// Updates clipping uniforms in all section-cut materials.
pub fn sync_section_cut_materials(
    section_planes: Res<'_, SectionPlanes>,
    mut materials: ResMut<'_, Assets<SectionCutMaterial>>,
    query: Query<
        '_,
        '_,
        (&StructuralElement, &MeshMaterial3d<SectionCutMaterial>),
        With<ElementMarker>,
    >,
) {
    if !section_planes.is_changed() {
        return;
    }

    for (element, material_handle) in &query {
        if let Some(material) = materials.get_mut(&material_handle.0) {
            material.params.base_color = element_color(element);
            material.params.plane_xy = Vec4::new(0.0, 0.0, 1.0, section_planes.xy_z);
            material.params.plane_xz = Vec4::new(0.0, 1.0, 0.0, section_planes.xz_y);
            material.params.plane_yz = Vec4::new(1.0, 0.0, 0.0, section_planes.yz_x);
            material.params.flags = Vec4::new(
                enabled(section_planes.xy_enabled),
                enabled(section_planes.xz_enabled),
                enabled(section_planes.yz_enabled),
                section_planes.depth.max(0.01),
            );
        }
    }
}

/// Updates section-plane quad transforms and visibility.
pub fn update_section_plane_visuals(
    section_planes: Res<'_, SectionPlanes>,
    mut query: Query<'_, '_, (&SectionPlaneVisual, &mut Transform, &mut Visibility)>,
) {
    if !section_planes.is_changed() {
        return;
    }

    for (plane, mut transform, mut visibility) in &mut query {
        match plane.kind {
            SectionPlaneVisualKind::XY => {
                *visibility = if section_planes.xy_enabled {
                    Visibility::Visible
                } else {
                    Visibility::Hidden
                };
                transform.translation = Vec3::new(10.0, 8.0, section_planes.xy_z);
                transform.rotation = Quat::from_rotation_x(std::f32::consts::FRAC_PI_2);
            }
            SectionPlaneVisualKind::XZ => {
                *visibility = if section_planes.xz_enabled {
                    Visibility::Visible
                } else {
                    Visibility::Hidden
                };
                transform.translation = Vec3::new(10.0, section_planes.xz_y, 76.0);
                transform.rotation = Quat::IDENTITY;
            }
            SectionPlaneVisualKind::YZ => {
                *visibility = if section_planes.yz_enabled {
                    Visibility::Visible
                } else {
                    Visibility::Hidden
                };
                transform.translation = Vec3::new(section_planes.yz_x, 8.0, 76.0);
                transform.rotation = Quat::from_rotation_z(-std::f32::consts::FRAC_PI_2);
            }
        }
    }
}

/// Handles keyboard shortcuts: Ctrl+1/2/3 toggle XY/XZ/YZ planes.
pub fn section_plane_shortcuts(
    keys: Res<'_, ButtonInput<KeyCode>>,
    mut section_planes: ResMut<'_, SectionPlanes>,
) {
    let ctrl = keys.pressed(KeyCode::ControlLeft) || keys.pressed(KeyCode::ControlRight);
    if !ctrl {
        return;
    }

    if keys.just_pressed(KeyCode::Digit1) {
        section_planes.xy_enabled = !section_planes.xy_enabled;
    }
    if keys.just_pressed(KeyCode::Digit2) {
        section_planes.xz_enabled = !section_planes.xz_enabled;
    }
    if keys.just_pressed(KeyCode::Digit3) {
        section_planes.yz_enabled = !section_planes.yz_enabled;
    }
}

/// Axis-aligned section-plane selector for 2D section view extraction.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ActivePlaneKind {
    XY,
    XZ,
    YZ,
}

/// 3D clip plane representation.
#[derive(Clone, Debug)]
pub struct ClipPlane {
    pub normal: Vector3<f64>,
    pub point: Point3<f64>,
}

impl ClipPlane {
    /// Returns signed distance from point to plane.
    pub fn signed_distance(&self, p: &Point3<f64>) -> f64 {
        self.normal.dot(&(p - self.point))
    }

    /// Computes segment-plane intersection point when endpoints are on opposite sides.
    pub fn intersect_segment(&self, a: &Point3<f64>, b: &Point3<f64>) -> Option<Point3<f64>> {
        let da = self.signed_distance(a);
        let db = self.signed_distance(b);
        if da.abs() < EPSILON {
            return Some(*a);
        }
        if db.abs() < EPSILON {
            return Some(*b);
        }
        if da * db > 0.0 {
            return None;
        }
        let t = da / (da - db);
        Some(Point3::from(a.coords + (b.coords - a.coords) * t))
    }
}

/// Intersection primitive used by 2D section-view rendering.
#[derive(Clone, Debug)]
pub enum SectionGeometry2D {
    Point([f64; 2]),
    Segment([f64; 2], [f64; 2]),
}

/// 2D intersection record for one structural element.
#[derive(Clone, Debug)]
pub struct SectionIntersection {
    pub element_id: u32,
    pub element_type: String,
    pub geometry: SectionGeometry2D,
}

/// Returns currently active axis plane and geometric clip plane.
pub fn active_clip_plane(section_planes: &SectionPlanes) -> Option<(ActivePlaneKind, ClipPlane)> {
    if section_planes.xy_enabled {
        return Some((
            ActivePlaneKind::XY,
            ClipPlane {
                normal: Vector3::new(0.0, 0.0, 1.0),
                point: Point3::new(0.0, 0.0, section_planes.xy_z as f64),
            },
        ));
    }
    if section_planes.xz_enabled {
        return Some((
            ActivePlaneKind::XZ,
            ClipPlane {
                normal: Vector3::new(0.0, 1.0, 0.0),
                point: Point3::new(0.0, section_planes.xz_y as f64, 0.0),
            },
        ));
    }
    if section_planes.yz_enabled {
        return Some((
            ActivePlaneKind::YZ,
            ClipPlane {
                normal: Vector3::new(1.0, 0.0, 0.0),
                point: Point3::new(section_planes.yz_x as f64, 0.0, 0.0),
            },
        ));
    }
    None
}

/// Projects a 3D point into 2D plane coordinates.
pub fn project_to_plane_coords(point: &Point3<f64>, kind: ActivePlaneKind) -> [f64; 2] {
    match kind {
        ActivePlaneKind::XY => [point.x, point.y],
        ActivePlaneKind::XZ => [point.x, point.z],
        ActivePlaneKind::YZ => [point.y, point.z],
    }
}

/// Extracts 2D section primitives by clipping project elements against an active plane.
pub fn extract_section_intersections(
    project: &Project,
    kind: ActivePlaneKind,
    plane: &ClipPlane,
    depth: f64,
) -> Vec<SectionIntersection> {
    let mut out = Vec::new();
    let tolerance = depth.max(0.001);

    for element in project.elements.values() {
        let Some(node_i) = project.nodes.get(&element.node_i) else {
            continue;
        };
        let Some(node_j) = project.nodes.get(&element.node_j) else {
            continue;
        };

        let a = Point3::new(node_i.x, node_i.y, node_i.z);
        let b = Point3::new(node_j.x, node_j.y, node_j.z);
        let da = plane.signed_distance(&a);
        let db = plane.signed_distance(&b);

        if da.abs() <= tolerance && db.abs() <= tolerance {
            out.push(SectionIntersection {
                element_id: element.id,
                element_type: element.element_type.as_str().to_string(),
                geometry: SectionGeometry2D::Segment(
                    project_to_plane_coords(&a, kind),
                    project_to_plane_coords(&b, kind),
                ),
            });
            continue;
        }

        if let Some(p) = plane.intersect_segment(&a, &b) {
            out.push(SectionIntersection {
                element_id: element.id,
                element_type: element.element_type.as_str().to_string(),
                geometry: SectionGeometry2D::Point(project_to_plane_coords(&p, kind)),
            });
        }
    }
    out
}

fn enabled(state: bool) -> f32 {
    if state { 1.0 } else { 0.0 }
}

fn element_color(element: &StructuralElement) -> Vec4 {
    match element.element_type {
        crate::ecs::components::ElementType::BeamX => Vec4::new(0.2, 0.6, 1.0, 0.35),
        crate::ecs::components::ElementType::BeamY => Vec4::new(0.2, 0.8, 0.6, 0.35),
        crate::ecs::components::ElementType::Column => Vec4::new(1.0, 0.3, 0.3, 0.35),
        crate::ecs::components::ElementType::BraceXZ => Vec4::new(1.0, 0.8, 0.2, 0.35),
        crate::ecs::components::ElementType::BraceYZ => Vec4::new(1.0, 0.5, 0.0, 0.35),
        crate::ecs::components::ElementType::BraceFloor => Vec4::new(0.6, 0.4, 0.8, 0.35),
        crate::ecs::components::ElementType::CoreWall => Vec4::new(0.5, 0.5, 0.5, 0.35),
        crate::ecs::components::ElementType::Chevron => Vec4::new(0.0, 0.8, 0.0, 0.35),
        crate::ecs::components::ElementType::BraceSpace => Vec4::new(1.0, 0.0, 1.0, 0.35),
        crate::ecs::components::ElementType::Custom(_) => Vec4::new(1.0, 1.0, 1.0, 0.35),
    }
}

#[cfg(test)]
mod tests {
    use super::{ActivePlaneKind, ClipPlane, project_to_plane_coords};
    use nalgebra::{Point3, Vector3};

    #[test]
    fn signed_distance_matches_plane_normal_direction() {
        let plane = ClipPlane {
            normal: Vector3::new(0.0, 0.0, 1.0),
            point: Point3::new(0.0, 0.0, 10.0),
        };
        assert!(plane.signed_distance(&Point3::new(0.0, 0.0, 12.0)) > 0.0);
        assert!(plane.signed_distance(&Point3::new(0.0, 0.0, 8.0)) < 0.0);
    }

    #[test]
    fn segment_intersection_exists_when_crossing_plane() {
        let plane = ClipPlane {
            normal: Vector3::new(1.0, 0.0, 0.0),
            point: Point3::new(0.0, 0.0, 0.0),
        };
        let p = plane
            .intersect_segment(&Point3::new(-1.0, 0.0, 0.0), &Point3::new(1.0, 0.0, 0.0))
            .expect("should intersect");
        assert!((p.x - 0.0).abs() < 1e-6);
    }

    #[test]
    fn projection_uses_expected_axes() {
        let p = Point3::new(4.0, 5.0, 6.0);
        assert_eq!(project_to_plane_coords(&p, ActivePlaneKind::XY), [4.0, 5.0]);
        assert_eq!(project_to_plane_coords(&p, ActivePlaneKind::XZ), [4.0, 6.0]);
        assert_eq!(project_to_plane_coords(&p, ActivePlaneKind::YZ), [5.0, 6.0]);
    }
}
