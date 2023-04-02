
init_source = """

#include <common>
#include <noise>
#include <sdf>

void main() {
    float seed = float(id.x) + rand(float(id.y));

    vec2 pos = rand_vec2(seed);
    float angle = rand(seed) * 2.0*PI;


    imageStore(data, id, vec4(pos, angle, 1.0));
}

"""

slime_source = """

float change_angle(float angle, vec2 pos) {
    float sample0 = texture(world_sampler, pos
        + vec2(cos(angle + SENSOR_ANGLE) * SENSOR_LEN,
               sin(angle + SENSOR_ANGLE) * SENSOR_LEN)).r;

    float sample1 = texture(world_sampler, pos
        + vec2(cos(angle - SENSOR_ANGLE) * SENSOR_LEN,
               sin(angle - SENSOR_ANGLE) * SENSOR_LEN)).r;

    if(sample0 > sample1)
        return angle + TURN_SPEED;
    else
        return angle - TURN_SPEED;
}

void main() {
    vec4 dat = imageLoad(data, id);
    
    vec2 pos = dat.xy;
    float angle = dat.z;

    pos = mod(pos + vec2(cos(angle), sin(angle)) * SPEED, 1.0);

    angle = change_angle(angle, pos);

    // if(new_pos.x < 0.0 || new_pos.y < 0.0 || new_pos.x > 1.0 || new_pos.y > 1.0)
    //     angle = rand(float(cell_id)) * 2.0*PI;
    // // else
    // pos = new_pos;

    imageStore(data, id, vec4(pos, angle, 1.0));
    imageStore(world, ivec2(pos * world_size), vec4(vec3(1.0), 1.0));
}

"""

blur_source = """

void main() {
    imageStore(world, id, 
        vec4((imageLoad(world, id) - REDUCTION).xyz, 1.0)
//               * vec4(1.0, 0.1, 0.3, 1.0)
               );
}

"""

from rhubarb.shader     import Shader
from rhubarb.uniform    import Uniform
from rhubarb.texture    import Texture

import math
import imgui

sensor_angle = Uniform("float", "SENSOR_ANGLE", 1.0)
sensor_len   = Uniform("float", "SENSOR_LEN",   0.1)
turn_speed   = Uniform("float", "TURN_SPEED",   1.0)
speed        = Uniform("float", "SPEED",        0.01)
reduction    = Uniform("float", "REDUCTION",    0.1)

# texture initialzation

data =  Texture("data",  (1000, 1000))
target = Texture("world", (1000, 1000))

setup     = Shader(init_source,  data.size) 
slimemold = Shader(slime_source, data.size)
blur      = Shader(blur_source,  target.size)

setup.dispatch()

max_fps = 300

def draw():
    slimemold.dispatch()
    blur.dispatch()

    imgui.begin("vars")
    
    _, turn_speed.val    = imgui.slider_float(
            "turn speed", turn_speed.val, 
            0.0, 1.0, "%.2f", 1.0)

    _, sensor_angle.val  = imgui.slider_float(
            "sensor angle", sensor_angle.val, 
            0.0, 1.0, "%.2f", 1.0)

    _, sensor_len.val = imgui.slider_float(
            "sensor length", sensor_len.val, 
            0.0, 0.1, "%.4f", 1.0)

    _, speed.val         = imgui.slider_float(
            "speed", speed.val, 
            0.0, 0.05, "%.4f", 1.0)

    _, reduction.val     = imgui.slider_float(
            "reduction", reduction.val, 
            0.0, 0.5, "%.2f", 1.0)

    imgui.end()

