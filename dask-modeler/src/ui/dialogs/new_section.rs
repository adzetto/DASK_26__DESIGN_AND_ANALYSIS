//! New section creation dialog.

use bevy::prelude::*;
use bevy_egui::{EguiContexts, egui};

use crate::ecs::resources::{NewSectionDialogState, ProjectResource, SectionShapeKind};
use crate::model::{SectionDef, SectionShape};

/// Draws section-definition dialog and inserts a new section into the project.
pub fn new_section_dialog_ui(
    mut contexts: EguiContexts<'_, '_>,
    mut state: ResMut<'_, NewSectionDialogState>,
    mut project_res: ResMut<'_, ProjectResource>,
) {
    if !state.open {
        return;
    }

    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    let mut open = state.open;
    let mut should_close = false;
    let mut create_requested = false;

    egui::Window::new("Yeni Kesit")
        .open(&mut open)
        .resizable(false)
        .show(ctx, |ui| {
            ui.label("Kesit geometrisini tanimla");
            ui.horizontal(|ui| {
                ui.label("Ad");
                ui.text_edit_singleline(&mut state.name);
            });

            egui::ComboBox::from_label("Sekil")
                .selected_text(shape_label(state.shape))
                .show_ui(ui, |ui| {
                    ui.selectable_value(
                        &mut state.shape,
                        SectionShapeKind::Rectangular,
                        shape_label(SectionShapeKind::Rectangular),
                    );
                    ui.selectable_value(
                        &mut state.shape,
                        SectionShapeKind::IBeam,
                        shape_label(SectionShapeKind::IBeam),
                    );
                    ui.selectable_value(
                        &mut state.shape,
                        SectionShapeKind::Circular,
                        shape_label(SectionShapeKind::Circular),
                    );
                    ui.selectable_value(
                        &mut state.shape,
                        SectionShapeKind::Pipe,
                        shape_label(SectionShapeKind::Pipe),
                    );
                    ui.selectable_value(
                        &mut state.shape,
                        SectionShapeKind::LAngle,
                        shape_label(SectionShapeKind::LAngle),
                    );
                });

            draw_shape_inputs(ui, &mut state);
            ui.horizontal(|ui| {
                ui.label("Renk");
                ui.color_edit_button_rgb(&mut state.color);
            });

            let shape = build_shape_from_state(&state);
            let preview = SectionDef::new(0, "preview", shape, state.color);
            ui.separator();
            ui.label(format!(
                "A={:.3}, Ix={:.3}, Iy={:.3}, J={:.3}",
                preview.area, preview.ix, preview.iy, preview.j
            ));
            draw_section_preview(ui, state.shape);

            ui.separator();
            ui.horizontal(|ui| {
                if ui.button("Olustur").clicked() {
                    create_requested = true;
                }
                if ui.button("Iptal").clicked() {
                    should_close = true;
                }
            });
        });

    if create_requested {
        let id = project_res.project.next_section_id;
        let name = if state.name.trim().is_empty() {
            format!("SEC-{id}")
        } else {
            state.name.trim().to_string()
        };
        let shape = build_shape_from_state(&state);
        project_res
            .project
            .insert_section(SectionDef::new(id, name, shape, state.color));
        should_close = true;
    }

    if should_close {
        open = false;
    }
    state.open = open;
}

fn shape_label(shape: SectionShapeKind) -> &'static str {
    match shape {
        SectionShapeKind::Rectangular => "Dikdortgen",
        SectionShapeKind::IBeam => "I-Kesit",
        SectionShapeKind::Circular => "Dairesel",
        SectionShapeKind::Pipe => "Boru",
        SectionShapeKind::LAngle => "L-Aci",
    }
}

fn draw_shape_inputs(ui: &mut egui::Ui, state: &mut NewSectionDialogState) {
    match state.shape {
        SectionShapeKind::Rectangular => {
            two_value_row(
                ui,
                "Genislik",
                &mut state.width,
                "Yukseklik",
                &mut state.height,
            );
        }
        SectionShapeKind::IBeam => {
            two_value_row(
                ui,
                "Baslik W",
                &mut state.flange_w,
                "Baslik T",
                &mut state.flange_t,
            );
            two_value_row(ui, "Govde H", &mut state.web_h, "Govde T", &mut state.web_t);
        }
        SectionShapeKind::Circular => {
            one_value_row(ui, "Cap", &mut state.diameter);
        }
        SectionShapeKind::Pipe => {
            two_value_row(
                ui,
                "Dis Cap",
                &mut state.outer_d,
                "Ic Cap",
                &mut state.inner_d,
            );
        }
        SectionShapeKind::LAngle => {
            two_value_row(ui, "Kol A", &mut state.leg_a, "Kol B", &mut state.leg_b);
            one_value_row(ui, "Et Kalinligi", &mut state.thickness);
        }
    }
}

fn one_value_row(ui: &mut egui::Ui, label: &str, value: &mut f64) {
    ui.horizontal(|ui| {
        ui.label(label);
        ui.add(
            egui::DragValue::new(value)
                .speed(0.1)
                .range(0.01..=10_000.0),
        );
    });
}

fn two_value_row(ui: &mut egui::Ui, label_a: &str, a: &mut f64, label_b: &str, b: &mut f64) {
    ui.horizontal(|ui| {
        ui.label(label_a);
        ui.add(egui::DragValue::new(a).speed(0.1).range(0.01..=10_000.0));
        ui.label(label_b);
        ui.add(egui::DragValue::new(b).speed(0.1).range(0.01..=10_000.0));
    });
}

fn build_shape_from_state(state: &NewSectionDialogState) -> SectionShape {
    match state.shape {
        SectionShapeKind::Rectangular => SectionShape::Rectangular {
            width: state.width.max(0.01),
            height: state.height.max(0.01),
        },
        SectionShapeKind::IBeam => SectionShape::IBeam {
            flange_w: state.flange_w.max(0.01),
            flange_t: state.flange_t.max(0.01),
            web_h: state.web_h.max(0.01),
            web_t: state.web_t.max(0.01),
        },
        SectionShapeKind::Circular => SectionShape::Circular {
            diameter: state.diameter.max(0.01),
        },
        SectionShapeKind::Pipe => SectionShape::Pipe {
            outer_d: state.outer_d.max(0.01),
            inner_d: state.inner_d.clamp(0.0, state.outer_d.max(0.01) - 0.001),
        },
        SectionShapeKind::LAngle => SectionShape::LAngle {
            leg_a: state.leg_a.max(0.01),
            leg_b: state.leg_b.max(0.01),
            thickness: state
                .thickness
                .clamp(0.01, state.leg_a.min(state.leg_b).max(0.01)),
        },
    }
}

fn draw_section_preview(ui: &mut egui::Ui, shape: SectionShapeKind) {
    let (response, painter) = ui.allocate_painter(egui::vec2(180.0, 120.0), egui::Sense::hover());
    let rect = response.rect.shrink(8.0);
    painter.rect_stroke(
        response.rect,
        4.0,
        egui::Stroke::new(1.0, egui::Color32::DARK_GRAY),
        egui::StrokeKind::Inside,
    );

    match shape {
        SectionShapeKind::Rectangular => {
            painter.rect_filled(rect, 0.0, egui::Color32::from_gray(120));
        }
        SectionShapeKind::IBeam => {
            let top = egui::Rect::from_min_max(rect.min, egui::pos2(rect.max.x, rect.min.y + 20.0));
            let bot = egui::Rect::from_min_max(egui::pos2(rect.min.x, rect.max.y - 20.0), rect.max);
            let web = egui::Rect::from_min_max(
                egui::pos2(rect.center().x - 10.0, rect.min.y + 20.0),
                egui::pos2(rect.center().x + 10.0, rect.max.y - 20.0),
            );
            painter.rect_filled(top, 0.0, egui::Color32::from_gray(120));
            painter.rect_filled(bot, 0.0, egui::Color32::from_gray(120));
            painter.rect_filled(web, 0.0, egui::Color32::from_gray(140));
        }
        SectionShapeKind::Circular => {
            painter.circle_filled(
                rect.center(),
                rect.width().min(rect.height()) * 0.45,
                egui::Color32::from_gray(125),
            );
        }
        SectionShapeKind::Pipe => {
            let r = rect.width().min(rect.height()) * 0.45;
            painter.circle_filled(rect.center(), r, egui::Color32::from_gray(130));
            painter.circle_filled(rect.center(), r * 0.55, egui::Color32::from_gray(35));
        }
        SectionShapeKind::LAngle => {
            let pts = vec![
                egui::pos2(rect.min.x, rect.min.y),
                egui::pos2(rect.min.x + 30.0, rect.min.y),
                egui::pos2(rect.min.x + 30.0, rect.max.y - 30.0),
                egui::pos2(rect.max.x, rect.max.y - 30.0),
                egui::pos2(rect.max.x, rect.max.y),
                egui::pos2(rect.min.x, rect.max.y),
            ];
            painter.add(egui::Shape::convex_polygon(
                pts,
                egui::Color32::from_gray(120),
                egui::Stroke::NONE,
            ));
        }
    }
}
