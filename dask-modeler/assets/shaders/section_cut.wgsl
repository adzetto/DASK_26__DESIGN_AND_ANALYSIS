#import bevy_pbr::forward_io::VertexOutput

struct SectionCutMaterial {
    base_color: vec4<f32>,
    plane_xy: vec4<f32>, // xyz = normal, w = distance
    plane_xz: vec4<f32>,
    plane_yz: vec4<f32>,
    flags: vec4<f32>,    // x,y,z = enabled, w = depth
};

@group(#{MATERIAL_BIND_GROUP}) @binding(0)
var<uniform> material: SectionCutMaterial;

@fragment
fn fragment(in: VertexOutput) -> @location(0) vec4<f32> {
    let world_pos = in.world_position.xyz;
    let depth = max(material.flags.w, 0.0001);

    if (material.flags.x > 0.5) {
        let signed_dist = dot(material.plane_xy.xyz, world_pos) - material.plane_xy.w;
        if (signed_dist > depth) {
            discard;
        }
    }
    if (material.flags.y > 0.5) {
        let signed_dist = dot(material.plane_xz.xyz, world_pos) - material.plane_xz.w;
        if (signed_dist > depth) {
            discard;
        }
    }
    if (material.flags.z > 0.5) {
        let signed_dist = dot(material.plane_yz.xyz, world_pos) - material.plane_yz.w;
        if (signed_dist > depth) {
            discard;
        }
    }

    return material.base_color;
}
