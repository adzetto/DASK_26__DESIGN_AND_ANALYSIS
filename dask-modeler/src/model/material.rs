//! Material definition model.

use serde::{Deserialize, Serialize};

/// Linear-elastic/plastic material metadata.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct MaterialDef {
    /// Unique material identifier.
    pub id: u32,
    /// Name used in UI/export.
    pub name: String,
    /// Young's modulus E.
    pub e: f64,
    /// Shear modulus G.
    pub g: f64,
    /// Poisson ratio ν.
    pub nu: f64,
    /// Density ρ.
    pub density: f64,
    /// Yield strength fy.
    pub fy: f64,
    /// Ultimate strength fu.
    pub fu: f64,
}

impl MaterialDef {
    /// Creates a material definition.
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        id: u32,
        name: impl Into<String>,
        e: f64,
        g: f64,
        nu: f64,
        density: f64,
        fy: f64,
        fu: f64,
    ) -> Self {
        Self {
            id,
            name: name.into(),
            e,
            g,
            nu,
            density,
            fy,
            fu,
        }
    }

    /// Returns the default DASK balsa material from config values.
    pub fn balsa_default(id: u32) -> Self {
        Self::new(id, "Balsa", 3500.0, 1346.0, 0.3, 160.0, 0.0, 0.0)
    }
}

#[cfg(test)]
mod tests {
    use super::MaterialDef;

    #[test]
    fn balsa_defaults_match_expected_moduli() {
        let balsa = MaterialDef::balsa_default(1);
        assert_eq!(balsa.e, 3500.0);
        assert_eq!(balsa.g, 1346.0);
    }
}
