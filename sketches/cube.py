
source = """

#include <common>
#include <noise>
#include <sdf>
#include <raymarching>

float scene_sdf(vec3 p) {
    return box_sdf(
            (p - vec3(5.0, 0.0, 0.0)),
            vec3(1.0, 1.2, 3.0));
}

void main() {
    vec2 uv = vec2(id) / vec2(target_size);

    vec2 project_plane = vec2(uv * 2.0 - 1.0);
    vec3 ro = vec3(0.0, 0.0, 0.0);// * rotateZ(time*2.0);
    vec3 rd = normalize(vec3(1.0, -project_plane));

    vec3 p = ray_march(ro, rd);
    vec3 d = get_normal(p);

    vec4 col = vec4(d * 0.5 + 0.5, 1.0);
    col.xyz *= rotate(noise_vec3(time * 0.2) * 2*PI);
    imageStore(target, id, col);
}

"""

from rhubarb.shader     import Shader
from rhubarb.texture    import Texture
from rhubarb.uniform    import Uniform

target = Texture("target", (1000, 1000))
cube = Shader(source, target.size) 

def draw():
    cube.dispatch()

