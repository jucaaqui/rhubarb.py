
init_source = """

void main() {
    vec4 val = vec4(1.0, 1.0, 1.0, 1.0);

    if (rand(vec2(id)) < 0.5)
        val = vec4(0.0, 0.0, 0.0, 1.0);

    imageStore(world, id, val);
}

"""

next_source = """

bool is_alive(ivec2 coord) {
    return imageLoad(world, coord).r == 1.0;
}
    
void main() {
    int neighbors = 0;

    if (is_alive(id + ivec2(-1, -1))) neighbors++;
    if (is_alive(id + ivec2(-1,  0))) neighbors++;
    if (is_alive(id + ivec2(-1,  1))) neighbors++;
    if (is_alive(id + ivec2( 0, -1))) neighbors++;
    if (is_alive(id + ivec2( 0,  1))) neighbors++;
    if (is_alive(id + ivec2( 1, -1))) neighbors++;
    if (is_alive(id + ivec2( 1,  0))) neighbors++;
    if (is_alive(id + ivec2( 1,  1))) neighbors++;

    vec2 uv = vec2(id) / vec2(world_size);

    if (neighbors <= 1 || neighbors >= 4)
        imageStore(buff, id, vec4(0.0, 0.0, 0.0, 1.0));
    else if (neighbors == 3)
        imageStore(buff, id, vec4(1.0, uv.x, uv.y, 1.0));
}

"""

swap_source = """
    
void main() {
    imageStore(world, id, imageLoad(buff, id));
}

"""

from rhubarb.texture import Texture
from rhubarb.shader  import Shader
from rhubarb.glsl    import common

target = Texture("world", (500, 500))
buff  = Texture("buff", target.size)

init = Shader(init_source, target.size, common)
next = Shader(next_source, target.size)
swap = Shader(swap_source, target.size)

max_fps = 300

init.dispatch()

def draw():
    next.dispatch()
    swap.dispatch()

