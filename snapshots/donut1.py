
source = """

#include <common>
#include <noise>
#include <sdf>
#include <raymarching>

float scene_sdf(vec3 p) {
    float scene = 10000.0;

    scene = min(scene,
        torus_sdf(fract(p + 0.5) - 0.5, vec2(0.2, 0.1)));
        //rand_vec2(rand(floor(p.xy + 0.5)) + 1.7) * 0.3 + 0.03));

    scene = min(scene,
        max(box_sdf(fract(p + 0.5) - 0.5 - vec3(0.0, 0.1, 0.0), 
                    vec3(0.5, 0.05, 0.5)), 
            torus_sdf(fract(p + 0.5) - 0.5, vec2(0.2, 0.105))));

    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(1.0, 0.0, 0.0),
                vec3(0.33)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 1.0, 0.0),
                vec3(0.33)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 0.0, 1.0),
                vec3(0.33)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(-1.0, 0.0, 0.0),
                vec3(0.33)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0,-1.0, 0.0),
                vec3(0.33)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 0.0,-1.0),
                vec3(0.33)));



    scene = max(scene,
        -box_sdf(p - vec3(0.0, 0.0, 0.0), vec3(0.5, 0.5, 100000.0)));

   // scene = max(scene,
   //     box_sdf(p - vec3(0.0, 0.0, 0.0), vec3(5.0, 5.0, 10000.0)));

    return scene;
}

void main() {
    vec2 uv = vec2(id - target_size*0.5) / target_size.y;

    vec2 project_plane = vec2(uv);
    vec3 ro = vec3(0.0, 0.0, mod(time * 0.4, 300.0));
    vec3 rd = normalize(vec3(0.5, -project_plane));

    vec3 theta = noise_vec3(time * 0.01) * 4.0*PI;

    //ro *= rotate(theta);
    rd *= rotate(theta);

    vec3 p = ray_march(ro, rd);
    vec3 d = get_normal(p);

    vec3 col = vec3(d * 0.5 + 0.5);
    vec3 base  = vec3(0.5, 0.4, 0.2) * length(col);
    vec3 icing = rand_vec3(rand(floor(p + 0.5) - 0.5)) * length(col);

    if (scene_sdf(p) > 50.0) 
        imageStore(target, id, vec4(0.0));
    else if (d.y > 0.41 || d.y == -1.0)
        imageStore(target, id, vec4(icing, 1.0));
    else
        imageStore(target, id, vec4(base, 1.0));
        
    //else if (abs(d.x) > abs(d.y) || abs(d.x) > abs(d.z))
    //    imageStore(target, id, imageLoad(vid3, id));
    //else if (abs(d.y) > abs(d.x) || abs(d.y) > abs(d.z))
    //    imageStore(target, id, imageLoad(vid2, id));
    //else if (abs(d.z) > abs(d.x) || abs(d.z) > abs(d.y))
    //    imageStore(target, id, imageLoad(vid3, id));
    //else
    //    imageStore(target, id, vec4(0.0));
        
    
}

"""

from rhubarb.shader  import Shader
from rhubarb.texture import Texture

target = Texture("target", (1920, 1080))

shader = Shader(source, target.size) 

def draw():
    shader.dispatch()

