//! Section geometry definitions and derived engineering properties.

use std::f64::consts::PI;

use serde::{Deserialize, Serialize};

/// Parametric section shape definitions.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub enum SectionShape {
    Rectangular {
        width: f64,
        height: f64,
    },
    IBeam {
        flange_w: f64,
        flange_t: f64,
        web_h: f64,
        web_t: f64,
    },
    Circular {
        diameter: f64,
    },
    Pipe {
        outer_d: f64,
        inner_d: f64,
    },
    LAngle {
        leg_a: f64,
        leg_b: f64,
        thickness: f64,
    },
}

/// Section definition including derived geometric properties.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct SectionDef {
    /// Unique section identifier.
    pub id: u32,
    /// Display name.
    pub name: String,
    /// Shape definition.
    pub shape: SectionShape,
    /// Area A.
    pub area: f64,
    /// Moment of inertia Ix.
    pub ix: f64,
    /// Moment of inertia Iy.
    pub iy: f64,
    /// Torsional constant J (approximate for open shapes).
    pub j: f64,
    /// RGB display color.
    pub color: [f32; 3],
}

impl SectionDef {
    /// Creates a section and computes area/inertia/torsion from shape geometry.
    pub fn new(id: u32, name: impl Into<String>, shape: SectionShape, color: [f32; 3]) -> Self {
        let (area, ix, iy, j) = shape_properties(&shape);
        Self {
            id,
            name: name.into(),
            shape,
            area,
            ix,
            iy,
            j,
            color,
        }
    }
}

fn shape_properties(shape: &SectionShape) -> (f64, f64, f64, f64) {
    match *shape {
        SectionShape::Rectangular { width, height } => {
            let area = width * height;
            let ix = width * height.powi(3) / 12.0;
            let iy = height * width.powi(3) / 12.0;
            let j = area * (width.powi(2) + height.powi(2)) / 12.0;
            (area, ix, iy, j)
        }
        SectionShape::IBeam {
            flange_w,
            flange_t,
            web_h,
            web_t,
        } => {
            let total_h = web_h + 2.0 * flange_t;
            let area = 2.0 * flange_w * flange_t + web_h * web_t;
            let ix = (flange_w * total_h.powi(3) - (flange_w - web_t) * web_h.powi(3)) / 12.0;
            let iy = (2.0 * flange_t * flange_w.powi(3) + web_h * web_t.powi(3)) / 12.0;
            let j = (2.0 * flange_w * flange_t.powi(3) + web_h * web_t.powi(3)) / 3.0;
            (area, ix, iy, j)
        }
        SectionShape::Circular { diameter } => {
            let area = PI * diameter.powi(2) / 4.0;
            let ix = PI * diameter.powi(4) / 64.0;
            let iy = ix;
            let j = PI * diameter.powi(4) / 32.0;
            (area, ix, iy, j)
        }
        SectionShape::Pipe { outer_d, inner_d } => {
            let area = PI * (outer_d.powi(2) - inner_d.powi(2)) / 4.0;
            let ix = PI * (outer_d.powi(4) - inner_d.powi(4)) / 64.0;
            let iy = ix;
            let j = PI * (outer_d.powi(4) - inner_d.powi(4)) / 32.0;
            (area, ix, iy, j)
        }
        SectionShape::LAngle {
            leg_a,
            leg_b,
            thickness,
        } => {
            // Composite rectangle method with overlap subtraction.
            let a1 = thickness * leg_b;
            let a2 = leg_a * thickness;
            let a3 = thickness * thickness;
            let area = a1 + a2 - a3;

            let x1 = thickness / 2.0;
            let y1 = leg_b / 2.0;
            let x2 = leg_a / 2.0;
            let y2 = thickness / 2.0;
            let x3 = thickness / 2.0;
            let y3 = thickness / 2.0;

            let cx = (a1 * x1 + a2 * x2 - a3 * x3) / area;
            let cy = (a1 * y1 + a2 * y2 - a3 * y3) / area;

            let ix1 = thickness * leg_b.powi(3) / 12.0 + a1 * (y1 - cy).powi(2);
            let ix2 = leg_a * thickness.powi(3) / 12.0 + a2 * (y2 - cy).powi(2);
            let ix3 = thickness * thickness.powi(3) / 12.0 + a3 * (y3 - cy).powi(2);
            let iy1 = leg_b * thickness.powi(3) / 12.0 + a1 * (x1 - cx).powi(2);
            let iy2 = thickness * leg_a.powi(3) / 12.0 + a2 * (x2 - cx).powi(2);
            let iy3 = thickness * thickness.powi(3) / 12.0 + a3 * (x3 - cx).powi(2);

            let ix = ix1 + ix2 - ix3;
            let iy = iy1 + iy2 - iy3;
            let j = (leg_a * thickness.powi(3) + leg_b * thickness.powi(3)) / 3.0;
            (area, ix, iy, j)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{SectionDef, SectionShape};

    #[test]
    fn rectangular_properties_are_positive() {
        let s = SectionDef::new(
            1,
            "R",
            SectionShape::Rectangular {
                width: 6.0,
                height: 6.0,
            },
            [0.6, 0.6, 0.6],
        );
        assert!(s.area > 0.0);
        assert!(s.ix > 0.0);
        assert!(s.iy > 0.0);
        assert!(s.j > 0.0);
    }
}
