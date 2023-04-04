
source = """

#include <common>
#include <noise>
#include <sdf>
#include <raymarching>

float scene_sdf(vec3 p) {
    return octahedron_sdf(p, 0.5);
}

void main() {
    vec2 uv = vec2(id - target_size.x / 2) / target_size.y;

    vec2 project_plane = vec2(uv * 2.0 - 1.0);
    vec3 ro = vec3(0.5, 0.0, 0.0);
    vec3 rd = normalize(vec3(1.0, -project_plane));

    vec3 p = ray_march(ro, rd);
    vec3 d = get_normal(p);

    vec3 col = vec3(d * 0.5 + 0.5);

    if (scene_sdf(p) > 50.0) col = normalize(p) * 0.5 + 0.5;

    imageStore(target, id, vec4(col, 1.0));
}

"""

from rhubarb.shader  import Shader
from rhubarb.texture import Texture

from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter


target = Texture("target", (1920, 1080))
vid0   = Texture("vid0", p0.size)
vid1   = Texture("vid1", p1.size)
vid2   = Texture("vid2", p2.size)

shader = Shader(source, target.size) 

#out = FFMPEG_VideoWriter("out.mov", target.size, 24)

#p0 = FFMPEG_VideoReader("resources/0.MOV")
#p1 = FFMPEG_VideoReader("resources/1.MOV")
#p2 = FFMPEG_VideoReader("resources/2.MOV")
#
#vid0.set_data(p0.read_frame())
#vid1.set_data(p1.read_frame())
#vid2.set_data(p2.read_frame())

def draw():
    shader.dispatch()
