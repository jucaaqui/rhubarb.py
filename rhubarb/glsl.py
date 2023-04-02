common = """

const float PI = 3.14159265359;

float rand(float x) {
    return fract(sin(x + 5173.34) * 1022985.92);
}

float rand(vec2 v) {
    return fract(sin(v.x - rand(v.y) + 117.34) * 6262.46);
}

float rand(vec3 v) {
    return fract(sin(v.x - rand(v.y) + 348.42*v.z) * 2341.34);
}

vec3 rand3(vec3 v) {
    return vec3(
        rand(v.x),
        rand(v.y),
        rand(v.z)
    );
}

vec3 rand_vec3(float x) {
    return vec3(
        fract(sin(x + 583.38) * 9859.23),
        fract(sin(x + 178.79) * 1527.22),
        fract(sin(x + 946.54) * 4033.16)
    );
}

vec2 rand_vec2(float x) {
    return vec2(
        fract(sin(x + 263.39) * 4519),
        fract(sin(x + 928.76) * 2852)
    );
}

mat3 rotateX(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(1, 0, 0),
        vec3(0, c, -s),
        vec3(0, s, c)
    );
}

// Rotation matrix around the Y axis.
mat3 rotateY(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(c, 0, s),
        vec3(0, 1, 0),
        vec3(-s, 0, c)
    );
}

// Rotation matrix around the Z axis.
mat3 rotateZ(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(c, -s, 0),
        vec3(s, c, 0),
        vec3(0, 0, 1)
    );
}

mat3 rotate(vec3 theta) {
    return rotateX(theta.x) * rotateY(theta.y) * rotateZ(theta.z);
}

float smin( float a, float b, float k ) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

float smoothmix(float a, float b, float x) {
    return (b - a) * (3*x*x - 2*x*x*x) + a;
}

vec2 rand_vec(vec2 p) {
    float theta = 2 * PI * rand(rand(p.x) - p.y);
    return vec2(cos(theta), sin(theta));
}

mat2 rotate(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat2(
        vec2(c,-s),
        vec2(s, c)
    );
}

// https://stackoverflow.com/questions/15095909/from-rgb-to-hsv-in-opengl-glsl
// All components are in the range [0…1], including hue.
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

float max3(vec3 v) {
    return max(max(v.x, v.y), v.z);
}

float min3(vec3 v) {
    return min(min(v.x, v.y), v.z);
}

float rgb2mono(vec3 c) {
    // return dot(c * vec3(0.2126, 0.7152, 0.0722), vec3(1.0));
    return dot(c * vec3(0.299, 0.587, 0.114), vec3(1.0));
    // return dot(c * vec3(0.3, 0.59, 0.11), vec3(1.0));
}

float smax(float a, float b, float k) {
    return -smin(-a, -b, k);
}

float sxor(float a, float b, float k) {
    float m = -smin(a, b, k);
    
    return smax(
        -smax(a, b, k), 
         smin(a, b, k), 
        k
    );
}

// tsl colourspace
// source: https://en.wikipedia.org/wiki/TSL_color_space
vec3 rgb2tsl(vec3 rgb) {
    float R = rgb.x / (dot(rgb, vec3(1.0))) - 1.0 / 3.0;
    float G = rgb.y / (dot(rgb, vec3(1.0))) - 1.0 / 3.0;
    
    // calculate tint
    float t;
    if(G > 0.0)
        t = (0.5 / PI) * atan(R / G) + 0.25;
    else if(G < 0.0)
        t = (0.5 / PI) * atan(R / G) + 0.75;
    else
        t = 0.0;
    
    //calculate saturation
    float s = sqrt(1.8 * (R*R + G*G));

    //calculate lightness
    float l = dot(rgb * vec3(0.2126, 0.7152, 0.0722), vec3(1.0));

    return vec3(t, s, l);
}

vec3 tsl2rgb(vec3 tsl) {
    float x = tan(2.0*PI * tsl.x - 0.5*PI);
    
    float G;
    if(tsl.x > 0.5)
        G = -sqrt(5.0 / (9.0*(x*x + 1.0))) * tsl.y;
    else if(tsl.x < 0.5)
        G = sqrt(5.0 / (9.0*(x*x + 1.0))) * tsl.y;
    else
        G = 0.0;

    float R;
    if(tsl.x == 0.0)
        R = sqrt(5.0) / 3.0 * tsl.y;
    else
        R = x * G;

    float r = R + 1.0 / 3.0;
    float g = G + 1.0 / 3.0;

    float k = tsl.z / (0.2126*r + 0.7152*g + 0.0722);

    return vec3(k * r, k * g, k * (1.0 - r - g));
}

float lerp(float p0, float p1, float t) {
    return p0 * t + p1 * (1 - t);
}

"""

noise = """

float noise(float x) {
    float f = (rand(floor(x)) * 2 - 1) * fract(x) + rand(floor(x + 1000.0)) - 0.5;
    
    float m = (rand(floor(x + 1)) * 2 - 1);
    float g = m * fract(x) - m + rand(floor(x + 1001.0)) - 0.5;

    return (smoothstep(1.0, 0.0, fract(x)) * f + smoothstep(0.0, 1.0, fract(x)) * g) * 0.5 + 0.5;
}

vec3 noise_vec3(float x) {
    return vec3(
        noise(x + 100.0), 
        noise(x + 200.0), 
        noise(x + 300.0)
    );
}

// Simplex 2D noise
//source: https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83
vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }

float snoise(vec2 v) {
    const vec4 C = vec4(0.211324865405187, 0.366025403784439,
            -0.577350269189626, 0.024390243902439);
    vec2 i  = floor(v + dot(v, C.yy) );
    vec2 x0 = v -   i + dot(i, C.xx);
    vec2 i1;
    i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;
    i = mod(i, 289.0);
    vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
    + i.x + vec3(0.0, i1.x, 1.0 ));
    vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
        dot(x12.zw,x12.zw)), 0.0);
    m = m*m ;
    m = m*m ;
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
    vec3 g;
    g.x  = a0.x  * x0.x  + h.x  * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
}

float loop_noise(float t, float r, float offset) {
    float angle = 2.0 * PI * t;
    return snoise(vec2(cos(angle) * r, sin(angle) * r + offset)) * 0.5 + 0.5;
}

vec2 loop_noise_vec2(float t, float r, float offset) {
    float angle = 2.0 * PI * t;
    vec2 p = vec2(cos(angle) * r, sin(angle) * r + offset);

    return vec2(
        snoise(p + vec2(10.0)),
        snoise(p + vec2(20.0))
    );
}

vec3 loop_noise_vec3(float t, float r, float offset) {
    float angle = 2.0 * PI * t;
    vec2 p = vec2(cos(angle) * r, sin(angle) * r + offset);

    return vec3(
        snoise(p + vec2(10.0)),
        snoise(p + vec2(20.0)),
        snoise(p + vec2(30.0))
    );
}

mat3 loop_rotate(float t, float r, float offset) {
    return rotate(mod(loop_noise_vec3(t, r, offset) * 5.0, 1.0) * 2.0*PI);
}


vec2 noise_vec2(float x) {
    return vec2(
        noise(x + 1000.0), 
        noise(x + 2000.0)
    );
}


float norm_snoise(vec2 p) {
    return snoise(p) * 0.5 + 0.5;
}

"""

pattern = """

float xadrez(vec2 p) {
    return abs(mod(p.x, 2.0) - 1.0) + abs(mod(p.y, 2.0) - 1.0) - 1.0;
}

float grid(vec2 p) {
    return abs(xadrez(p * rotate(radians(45))));
}

float hills(vec2 p) {
    return (sin(p.x) + sin(p.y)) * 0.5;
}

float copacabana(vec2 p, float A) {
    return sin(p.y - A * sin(p.x));
}

"""

raymarching = """

const int MAX_MARCHES = 500;
const float MAX_DIST = 100.0;
const float MIN_DIST = 0.001;

float scene_sdf(vec3 p);

vec3 ray_march(vec3 ro, vec3 rd) {
    vec3 p = ro;

    for(int i = 0; i < MAX_MARCHES; i++) {
        float d = scene_sdf(p);
        p = p + d * rd;
        if(d > MAX_DIST || d < MIN_DIST) break;
    }
    
    return p;
}

vec3 get_normal(vec3 p) {
    float d = scene_sdf(p);
    vec2 e = vec2(MIN_DIST, 0);

    vec3 n = d - vec3(
        scene_sdf(p - e.xyy),
        scene_sdf(p - e.yxy),
        scene_sdf(p - e.yyx)
    );
    
    return normalize(n);
}

"""

sdf = """

// raymarching SDFs //

float sphere_sdf(vec3 p, float r) {
    return length(p) - r;
}

float circle_sdf(vec2 p, float r) {
    return length(p) - r;
}

float box_sdf(vec3 p, vec3 b) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

float torus_sdf(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz)-t.x,p.y);
    return length(q)-t.y;
}

float line_sdf(vec3 p, vec3 a, vec3 b, float r) {
    vec3 pa = p - a, ba = b - a;
    float h = clamp(dot(pa,ba) / dot(ba,ba), 0.0, 1.0);
    return length(pa - ba*h) - r;
}

float prism_sdf(vec3 p, vec2 h) {
    vec3 q = abs(p);
    return max(q.z-h.y,max(q.x*0.866025+p.y*0.5,-p.y)-h.x*0.5);
}

float box_frame_sdf(vec3 p, vec3 b, float e) {
        p = abs(p  )-b;
    vec3 q = abs(p+e)-e;
    return min(min(
        length(max(vec3(p.x,q.y,q.z),0.0))+min(max(p.x,max(q.y,q.z)),0.0),
        length(max(vec3(q.x,p.y,q.z),0.0))+min(max(q.x,max(p.y,q.z)),0.0)),
        length(max(vec3(q.x,q.y,p.z),0.0))+min(max(q.x,max(q.y,p.z)),0.0));
}

// random SDFs

float random_sphere_sdf(vec3 p, float seed) {
    return sphere_sdf(
        (p + noise_vec3(seed) * 2.0 - 1.0),
        max(noise(seed) * 0.8 - 0.2, 0.05)
    );
}

float random_box_sdf(vec3 p, float seed) {
    return box_sdf(
        p * rotate(mod(noise_vec3(seed * 0.2 + 149.2) * 5.0, 1.0) * 2*PI) + (noise_vec3(seed + 701.4) * 2.0 - 1.0) * 0.8,
        vec3(
            max(noise(seed + 111.1) * 0.9 - 0.2, 0.05),
            max(noise(seed + 222.2) * 0.9 - 0.2, 0.05),
            max(noise(seed + 333.3) * 0.9 - 0.2, 0.05)
        )
    );
}

float random_torus_sdf(vec3 p, float seed) {
    return torus_sdf(
        (p * rotate(mod(noise_vec3(seed * 0.2 + 345.0) * 5.0, 1.0) * 2*PI) + noise_vec3(seed + 340.0) * 2.0 - 1.0),
        vec2(
            noise(seed + 444.4) * 0.7,
            max(noise(seed + 333.3) * 0.5 - 0.2, 0.05)
        )
    );
}

float random_line_sdf(vec3 p, float seed) { 
    return line_sdf(
        p,
        (noise_vec3(seed + 888.8) * 2.0 - 1.0) * 1.3,
        (noise_vec3(seed + 666.6) * 2.0 - 1.0) * 1.3,
        max(noise(seed) * 0.4 - 0.2, 0.05)
    );
}

float random_prism_sdf(vec3 p, float seed) { 
    return prism_sdf(
        p * rotate(mod(noise_vec3(seed * 0.2 + 521.1) * 5.0, 1.0) * 2*PI) + (noise_vec3(seed + 931.4) * 2.0 - 1.0) * 0.8,
        vec2(
            max(noise(seed + 222.2) - 0.2, 0.05),
            max(noise(seed + 333.3) - 0.2, 0.05)
        )
    );
}

"""

shapes = """

float circle_sdf(vec2 p, float r) {
    return length(p) - r;
}

float copacabana(vec2 p, float A, float T, float k) {
    return mod(p.y + A * sin(2.0 * PI * p.x / T), k) / k;
}

float xadrez(vec2 p) {
    float x = mod(p.x, 1.0) - 0.5;
    float y = mod(p.y, 1.0) - 0.5;

    return min(max(x, y), -min(x, y));
}

"""
