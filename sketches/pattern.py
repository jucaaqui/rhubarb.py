
source = """

#include <common>
#include <noise>

float n(vec2 p) {
    return mod(snoise(p) + snoise(vec2(time*0.01, p.x)), 0.4) < 0.2 ? 1.0 : 0.0;
}

vec2 w(vec2 p, float t) {
    return (p - noise_vec2(t)) 
         * noise_vec2(t)*10.0 
         * rotate(noise(t) * 2.0*PI);
}

vec3 get_col(vec2 p) {

    //vec3 col = vec3(1.0);

    //if (mod(snoise(vec2(uv.y, time * 0.01 + 000.0)), 0.5) > 0.25)
    //    col.r = 0.0;

    //if (mod(snoise(vec2(uv.y, time * 0.01 + 100.0)), 0.5) > 0.25)
    //    col.g = 0.0;
    //    
    //if (mod(snoise(vec2(uv.y, time * 0.01 + 200.0)), 0.5) > 0.25)
    //    col.b = 0.0;

    //if (mod(snoise(vec2(uv.x, time * 0.01 + 300.0)), 0.5) > 0.25)
    //    col.r = 0.0;

    //if (mod(snoise(vec2(uv.x, time * 0.01 + 400.0)), 0.5) > 0.25)
    //    col.g = 0.0;
    //    
    //if (mod(snoise(vec2(uv.x, time * 0.01 + 500.0)), 0.5) > 0.25)
    //    col.b = 0.0;

    vec3 col = vec3(n(p), n(p + 100.0), n(p + 200.0));

    vec2 q = w(p, time);

    if (pow(w(p, time*0.2), vec2(2)).x < p.x ^^ pow(w(p, time*0.1 + 100), vec2(2)).x < p.x ^^ pow(w(p, time*0.1 + 200), vec2(2)).x < p.x)

        col = vec3(n(p + 300.0), n(p + 400.0), n(p + 500.0));

    return hsv2rgb(rgb2hsv(col) * rotate(noise_vec3(time * 0.05) * 2*PI));
}

void main() {

    vec2 uv = vec2(id) / vec2(target_size); 

    imageStore(target, id, vec4(get_col(uv), 1.0));
}

"""

from rhubarb.texture import Texture
from rhubarb.shader  import Shader

target = Texture("target", (1000, 1000))
shader = Shader(source, target.size)

def draw():
    shader.dispatch()
