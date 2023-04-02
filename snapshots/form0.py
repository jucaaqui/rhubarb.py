
source = """

#include <common>
#include <noise>
#include <sdf>
#include <raymarching>

float scene_sdf(vec3 p) {
        

    float scene = 1000.0;

    float s = (sin(time)*0.5+0.5) * 2.0 + 0.5;

    scene = smin(scene, sphere_sdf(
        p - (noise_vec3(time*0.1)*2.0-1.0)*5.0, 
        2.0), s);
    scene = smin(scene, sphere_sdf(
        p - (noise_vec3(time*0.1 + 100.0)*2.0-1.0)*5.0, 
        2.0), s);

    scene = smin(scene, sphere_sdf(
        p - (noise_vec3(time*0.1 + 200.0)*2.0-1.0)*5.0, 
        2.0), s);

    return scene;
}

void main() {
    vec2 uv = vec2(id) / vec2(target_size);

    vec2 project_plane = vec2(uv * 2.0 - 1.0);
    vec3 ro = vec3(-20.0, 0.0, 0.0);
    vec3 rd = normalize(vec3(5.0, -project_plane));

    vec3 p = ray_march(ro, rd);
    vec3 d = get_normal(p);

    vec3 col = vec3(p * 0.5 + 0.5);

    //d *= rotateY(time*0.05);

    //if ((mod(atan(d.x / d.y) / PI, 0.1) < 0.05) ^^ 
    //    (mod(asin(d.z)       / PI, 0.1) < 0.05))
    //    
    //    col *= 0.>75;
    
    //if (scene_sdf(p) > 10.0) col = vec3(0.0);

    imageStore(target, id, vec4(col, 1.0));
}

"""

from rhubarb.shader  import Shader
from rhubarb.texture import Texture

target = Texture("target", (1000, 1000))
cube = Shader(source, target.size) 

def draw():
    cube.dispatch()
