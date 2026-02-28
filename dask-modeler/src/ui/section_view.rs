//! 2D section view panel.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::resources::{ProjectResource, SectionPlanes};
use crate::ecs::systems::section_cut::{
    SectionGeometry2D, active_clip_plane, extract_section_intersections,
};

/// Draws the extracted 2D section view of intersections on the active clip plane.
pub fn section_view_ui(
    mut contexts: EguiContexts<'_, '_>,
    project: Res<'_, ProjectResource>,
    planes: Res<'_, SectionPlanes>,
) {
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    egui::Window::new("Kesit Gorunumu")
        .default_size(egui::vec2(360.0, 260.0))
        .show(ctx, |ui| {
            let Some((kind, plane)) = active_clip_plane(&planes) else {
                ui.label("2B kesisimleri gormek icin XY, XZ veya YZ duzlemini acin.");
                return;
            };

            let intersections =
                extract_section_intersections(&project.project, kind, &plane, planes.depth as f64);

            ui.label(format!("Kesisim adedi: {}", intersections.len()));
            let desired = ui
                .available_size_before_wrap()
                .max(egui::vec2(200.0, 160.0));
            let (response, painter) = ui.allocate_painter(desired, egui::Sense::hover());
            let rect = response.rect;

            if intersections.is_empty() {
                painter.text(
                    rect.center(),
                    egui::Align2::CENTER_CENTER,
                    "Kesisim yok",
                    egui::FontId::default(),
                    egui::Color32::GRAY,
                );
                return;
            }

            let bounds = bounds_2d(&intersections);
            let map = |p: [f64; 2]| -> egui::Pos2 {
                let pad = 10.0_f32;
                let min_x = bounds.0[0] as f32;
                let min_y = bounds.0[1] as f32;
                let max_x = bounds.1[0] as f32;
                let max_y = bounds.1[1] as f32;
                let span_x = (max_x - min_x).max(1e-3);
                let span_y = (max_y - min_y).max(1e-3);
                let sx = (rect.width() - 2.0 * pad) / span_x;
                let sy = (rect.height() - 2.0 * pad) / span_y;
                let s = sx.min(sy);
                let x = rect.left() + pad + ((p[0] as f32 - min_x) * s);
                let y = rect.bottom() - pad - ((p[1] as f32 - min_y) * s);
                egui::pos2(x, y)
            };

            painter.rect_stroke(
                rect,
                0.0,
                egui::Stroke::new(1.0, egui::Color32::DARK_GRAY),
                egui::StrokeKind::Inside,
            );

            for isec in &intersections {
                let color = color_for_type(&isec.element_type);
                match &isec.geometry {
                    SectionGeometry2D::Point(p) => {
                        painter.circle_filled(map(*p), 2.2, color);
                    }
                    SectionGeometry2D::Segment(a, b) => {
                        painter.line_segment([map(*a), map(*b)], egui::Stroke::new(1.8, color));
                    }
                }
            }
        });
}

fn bounds_2d(
    intersections: &[crate::ecs::systems::section_cut::SectionIntersection],
) -> ([f64; 2], [f64; 2]) {
    let mut min = [f64::INFINITY, f64::INFINITY];
    let mut max = [f64::NEG_INFINITY, f64::NEG_INFINITY];

    for isec in intersections {
        match &isec.geometry {
            SectionGeometry2D::Point(p) => update_bounds(&mut min, &mut max, *p),
            SectionGeometry2D::Segment(a, b) => {
                update_bounds(&mut min, &mut max, *a);
                update_bounds(&mut min, &mut max, *b);
            }
        }
    }
    (min, max)
}

fn update_bounds(min: &mut [f64; 2], max: &mut [f64; 2], p: [f64; 2]) {
    min[0] = min[0].min(p[0]);
    min[1] = min[1].min(p[1]);
    max[0] = max[0].max(p[0]);
    max[1] = max[1].max(p[1]);
}

fn color_for_type(kind: &str) -> egui::Color32 {
    match kind {
        "beam_x" => egui::Color32::from_rgb(50, 153, 255),
        "beam_y" => egui::Color32::from_rgb(50, 204, 153),
        "column" => egui::Color32::from_rgb(255, 77, 77),
        "brace_xz" => egui::Color32::from_rgb(255, 204, 51),
        "brace_yz" => egui::Color32::from_rgb(255, 140, 0),
        "brace_floor" => egui::Color32::from_rgb(153, 102, 204),
        "core_wall" => egui::Color32::from_rgb(130, 130, 130),
        "chevron" => egui::Color32::from_rgb(0, 204, 0),
        "brace_space" => egui::Color32::from_rgb(255, 0, 255),
        _ => egui::Color32::WHITE,
    }
}
