
source = """

float scene_sdf(vec3 p) {
    float scene = 10000.0;

    scene = min(scene,
        box_sdf(fract(p + 0.5) - 0.5, 
        noise_vec3(rand(floor(p.xyz + 0.5)) + amp * 5.0) * 0.4 + 0.09));

    float k = 0.49;

    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(1.0, 0.0, 0.0),
                vec3(k)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 1.0, 0.0),
                vec3(k)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 0.0, 1.0),
                vec3(k)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(-1.0, 0.0, 0.0),
                vec3(k)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0,-1.0, 0.0),
                vec3(k)));
    scene = min(scene, 
                box_sdf((fract(p + 0.5) - 0.5) - vec3(0.0, 0.0,-1.0),
                vec3(k)));

    scene = max(scene,
        box_sdf(p - vec3(1000.0, 1000.0, 1000.0), vec3(1000.0, 1000.0, 1000.0)));


/*
    scene = max(scene,
        box_sdf(p - vec3(0.0, 0.0, 0.0), vec3(10.0, 10.0, 10.0)));
*/

    return scene;
}

vec4 get_col(vec2 xy) {
    xy *= vec2(1.0, -1.0);

    vec3 ro = vec3(-5.0, 0.0, 0.0);
    vec3 rd = normalize(vec3(2.0, -xy));

    //vec3 theta = noise_vec3(time * 0.002) * 4.0*PI;

    vec3 theta = vec3(0, -15 - 30*t, 45);
    theta = radians(theta);

    ro *= rotate(theta);
    rd *= rotate(theta);

    ro += vec3(0.0, 0.0, t * 50.0);

    vec3 p = ray_march(ro, rd);
    vec3 d = get_normal(p);

    vec3 col = vec3(d * 0.5 + 0.5);

    if (scene_sdf(p) > 50.0) 
        //return vec4(0.2);
        return imageLoad(vid0, id);
    else if (abs(d.x) > abs(d.y) || abs(d.x) > abs(d.z))
        //return vec4(0.4);
        return imageLoad(vid1, id);
    else if (abs(d.y) > abs(d.x) || abs(d.y) > abs(d.z))
        //return vec4(0.6);
        return imageLoad(vid2, id);
    else if (abs(d.z) > abs(d.x) || abs(d.z) > abs(d.y))
        //return vec4(0.8);
        return imageLoad(vid3, id);
}

void main() {
    vec2 xy = vec2(id - target_size*0.5) / target_size.y;


    vec2 pix_dim = 1.0 / target_size;

    vec4 col = (
          get_col(xy + vec2(0.0, 0.0) * pix_dim)
        + get_col(xy + vec2(0.0, 0.5) * pix_dim)
        + get_col(xy + vec2(0.5, 0.0) * pix_dim)
        + get_col(xy + vec2(0.5, 0.5) * pix_dim)) * 0.25;

    imageStore(target, id, col);
}

"""

from rhubarb.shader  import *
from rhubarb.texture import *
from rhubarb.uniform import *
from rhubarb.glsl    import *
from rhubarb.video   import *

import scipy.io.wavfile
import numpy as np
import math

from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter

last_frame = 24 * 60 * 5

target = Texture("target", (1920, 1080))
vid0   = Texture("vid0", target.size)
vid1   = Texture("vid1", target.size)
vid2   = Texture("vid2", target.size)
vid3   = Texture("vid3", target.size)

amp = Uniform("float", "amp", 0.01)
t   = Uniform("float", "t", 0.0)

shader = Shader(source, target.size, 
                  COMMON
                + NOISE
                + SDF
                + RAYMARCHING)

p0 = FFMPEG_VideoReader("res/d.MOV")
p1 = FFMPEG_VideoReader("res/a.MOV")
p2 = FFMPEG_VideoReader("res/b.MOV")
p3 = FFMPEG_VideoReader("res/c.MOV")

vid0.set_data(p0.read_frame())
vid1.set_data(p1.read_frame())
vid2.set_data(p2.read_frame())
vid3.set_data(p3.read_frame())

_, audio = scipy.io.wavfile.read('res/3.wav')

shader.dispatch()

out = VideoOut(target.size, 24, "out.mov")

i = 0

def draw():
    global i

    t.val = i / last_frame

    amp.val = math.sqrt(np.mean(np.square(
        audio[2000*i - 2000:2000*i + 2000]
        .astype(np.int32)))) / 13952.90

    vid0.set_data(p0.read_frame())
    vid1.set_data(p1.read_frame())
    vid2.set_data(p2.read_frame())
    vid3.set_data(p3.read_frame())

    if i % int(p0.duration*24) == 0: p0.initialize()
    if i % int(p1.duration*24) == 0: p1.initialize()
    if i % int(p2.duration*24) == 0: p2.initialize()
    if i % int(p3.duration*24) == 0: p3.initialize()

    shader.dispatch()

    out.write(target.get_data())

    i += 1
