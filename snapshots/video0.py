
source = """

#include <common>
#include <noise>
#include <sdf>
#include <raymarching>

float scene_sdf(vec3 p) {
    float scene = 10000.0;

    scene= min(scene, sphere_sdf((fract(p + 0.5) - 0.5), 0.1));

    scene = max(scene,
        -box_sdf(p - vec3(0.0, 0.0, 0.0), vec3(0.5, 0.5, 100000.0)));

    return scene;
    //return octahedron_sdf(p, 0.5);
    //float scene = 10000.0;

    //scene = min(scene,
    //    torus_sdf(fract(p + 0.5) - 0.5, vec2(0.2, 0.1)));
    //    //rand_vec2(rand(floor(p.xy + 0.5)) + 1.7) * 0.3 + 0.03));



    //scene = min(scene, 
    //            box_sdf((fract(p + 0.5) - 0.5) - vec3(1.0, 0.0, 0.0),
    //            vec3(0.33)));
    //scene = min(scene, 
    //            box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 1.0, 0.0),
    //            vec3(0.33)));
    //scene = min(scene, 
    //            box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 0.0, 1.0),
    //            vec3(0.33)));
    //scene = min(scene, 
    //            box_sdf((fract(p + 0.5) - 0.5) - vec3(-1.0, 0.0, 0.0),
    //            vec3(0.33)));
    //scene = min(scene, 
    //            box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0,-1.0, 0.0),
    //            vec3(0.33)));
    //scene = min(scene, 
    //            box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 0.0,-1.0),
    //            vec3(0.33)));



    //scene = max(scene,
    //    -box_sdf(p - vec3(0.0, 0.0, 0.0), vec3(0.5, 0.5, 100000.0)));

    //scene = max(scene,
    //    box_sdf(p - vec3(0.0, 0.0, 0.0), vec3(5.0, 5.0, 10000.0)));

    //return scene;
}

float sprinkles(vec3 p) {
    return sphere_sdf((fract(p + 0.5) - 0.5) * 100.0, 0.5);
}

void main() {
    vec2 uv = vec2(id - target_size*0.5) / target_size.y;

    vec2 project_plane = vec2(uv);
    vec3 ro = vec3(0.0, 0.0, mod(time * 0.4, 300.0));
    vec3 rd = normalize(vec3(3.0, -project_plane));

    vec3 theta = noise_vec3(time * 0.01) * 4.0*PI;

    //ro *= rotate(theta);
    rd *= rotate(theta);

    vec3 p = ray_march(ro, rd);
    vec3 d = get_normal(p);

    vec3 col = length(vec3(d * 0.5 + 0.5)) * vec3(0.5, 0.4, 0.2);
    vec3 icing = vec3(1.0, 0.9, 0.9);

    if (scene_sdf(p) > 50.0) 
        imageStore(target, id, imageLoad(vid0, id));
    else if (d.y > abs(d.x) || d.y > abs(d.z))
        if (sprinkles(p) < 0.0)
            imageStore(target, id, vec4(vec3(0.0), 1.0));
        else
            imageStore(target, id, vec4(icing, 1.0));
    else
        imageStore(target, id, vec4(col, 1.0));
        
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

from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter

target = Texture("target", (1920, 1080))
vid0   = Texture("vid0", target.size)
vid1   = Texture("vid1", target.size)
vid2   = Texture("vid2", target.size)
vid3   = Texture("vid3", target.size)

shader = Shader(source, target.size) 

#out = FFMPEG_VideoWriter("out.mov", target.size, 24)

p0 = FFMPEG_VideoReader("resources/0.MOV")
#p1 = FFMPEG_VideoReader("resources/1.MOV")
#p2 = FFMPEG_VideoReader("resources/2.MOV")
#p3 = FFMPEG_VideoReader("resources/3.MOV")

vid0.set_data(p0.read_frame())
shader.dispatch()

def draw():
    vid0.set_data(p0.read_frame())
    shader.dispatch()

