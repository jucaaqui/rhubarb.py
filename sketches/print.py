
source = """

float scene_sdf(vec3 p) {
    float scene = 1000.0;

    scene = min(scene,
        box_sdf(fract(p + 0.5) - 0.5, 
        rand_vec3(rand(floor(p.xy + 0.5)) + 1.7) * 0.3 + 0.03));

    scene = min(scene, 
        -box_sdf(fract(p + 0.5), vec3(1.001)));

    scene = max(scene,
        -box_sdf(p - vec3(0.0, 0.0, 0.0), vec3(1.5)));

    scene = max(scene,
        box_sdf(p - vec3(0.0, 0.0, 0.0), vec3(5.0 , 5.0, 100.0)));

    return scene;
}

vec3 get_col(vec2 uv) {
    vec2 project_plane = vec2(uv * 2.0 - 1.0);
    vec3 ro = vec3(0.0, 0.0, 0.0);
    vec3 rd = normalize(vec3(3.0, -project_plane));

    rd *= rotateY(radians(45));
    rd *= rotateZ(radians(45));

    vec3 p = ray_march(ro, rd);
    vec3 d = get_normal(p);

    vec3 col = vec3(1.0);

    if (d == vec3(0.0, -1.0, 0.0)) col = vec3(0.0);
    if (scene_sdf(p) > 100.0) col = vec3(0.0);

    return col;
}

void main() {
    vec2 uv = vec2(id) / target_size.y 
        + vec2(0.15, 0.0);
    vec2 pix_dim = 1.0 / target_size;

    vec3 col = (
          get_col(uv + vec2(0.0, 0.0) * pix_dim)
        + get_col(uv + vec2(0.0, 0.5) * pix_dim)
        + get_col(uv + vec2(0.5, 0.0) * pix_dim)
        + get_col(uv + vec2(0.5, 0.5) * pix_dim)) * 0.25;


    imageStore(target, id, vec4(col, 1.0));
}

"""

from rhubarb.shader  import Shader
from rhubarb.texture import Texture
from rhubarb.glsl    import common, noise, sdf, raymarching

target = Texture("target", (1000, 1000))
cube = Shader(source, target.size, 
              common + noise + sdf + raymarching) 

cube.dispatch()

