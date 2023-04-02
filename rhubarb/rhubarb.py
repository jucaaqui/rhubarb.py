import sys
import os
import importlib
import numpy as np
import traceback
import time
import pathlib

from OpenGL.GL import *
from glfw.GLFW import *

import imgui
import imgui.integrations.glfw

from rhubarb.shader    import *
from rhubarb.uniform   import *
from rhubarb.texture   import *
from rhubarb.constants import *

VERT_SOURCE = """

#version 330 core 

layout (location = 0) in vec2 vert_pos;
layout (location = 1) in vec2 tex_pos;

out vec2 uv;

void main() {
    gl_Position = vec4(vert_pos, 0, 1.0);
    uv = tex_pos;
}
    
"""

FRAG_SOURCE = """

#version 330 core

uniform sampler2D target_sampler;

in vec2 uv;

void main() {
    gl_FragColor = texture(target_sampler, uv);
}
    
"""

RHUBARB_COLOUR = (0.47, 0.13, 0.19)
RHUBARB_ACSENT = (0.78, 0.16, 0.25)

def update_sketch(sketch_source, _sketch, program):
    sketch_file = open(SKETCH_PATH, "w")
    sketch_file.write(sketch_source)
    sketch_file.close()

    Texture.textures = []
    Uniform.uniforms = [Shader.time, Shader.frame]

    importlib.reload(_sketch)

    glUseProgram(program)
    glUniform1i(glGetUniformLocation(program, "target_sampler"), 
                _sketch.target.unit)
    # returns min_draw_time
    return 1.0 / _sketch.max_fps
    
def parse_error(e):
    if type(e) == GLSLCompileError:
        return str(e)
    else: 
        stacktrace = traceback.format_exception(type(e), e,
                                                e.__traceback__)
        start = 0

        for i in range(len(stacktrace)):
            if "_sketch.py" in stacktrace[i]:
                start = i

        return "".join(stacktrace)

def main():
    os.chdir(PROJECT_DIR)

    if not glfwInit(): sys.exit("glfw did not initialize!")

    window = glfwCreateWindow(1920, 1080, "rhubarb", None, None)

    glfwMakeContextCurrent(window)

    def cbfun(window, width, height):
        glViewport(0, 0, width, height)

    glfwSetFramebufferSizeCallback(window, cbfun)

    vertices = (
        -1.0, -1.0, 0.0, 1.0,
        -1.0,  1.0, 0.0, 0.0,
         1.0,  1.0, 1.0, 0.0,
        -1.0, -1.0, 0.0, 1.0,
         1.0, -1.0, 1.0, 1.0,
         1.0,  1.0, 1.0, 0.0
    )

    vertices = np.array(vertices, dtype = np.float32)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, 
                 vertices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 
                          vertices.itemsize * 4, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 
                          vertices.itemsize * 4, ctypes.c_void_p(8))

    program = glCreateProgram()

    vert_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vert_shader, VERT_SOURCE)
    glCompileShader(vert_shader)
    glAttachShader(program, vert_shader)
    glDeleteShader(vert_shader)

    frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(frag_shader, FRAG_SOURCE)
    glCompileShader(frag_shader)
    glAttachShader(program, frag_shader)
    glDeleteShader(frag_shader)
    
    glBindAttribLocation(program, 0, "vPosition")
    glLinkProgram(program)

    error = ""
    old_sketch_source = open("rhubarb/basesketch.py").read()

    sketch_file = open(SKETCH_PATH, "w")
    sketch_file.write(old_sketch_source)
    sketch_file.close()

    from rhubarb import _sketch

    imgui.create_context()
    impl = imgui.integrations.glfw.GlfwRenderer(window)

    io = imgui.get_io()
    cascadia_code = io.fonts.add_font_from_file_ttf(
        "rhubarb/resources/CascadiaCode.ttf", 20)
    impl.refresh_font_texture()

    def cbfun(win, width, height):
        max_size = glfwGetWindowSize(window)

        max_ratio = max_size[0] / max_size[1]
        win_ratio = _sketch.target.size[0] / _sketch.target.size[1]

        if win_ratio < max_ratio:
            width = round(max_size[1] * win_ratio)
            height = max_size[1]
        else:
            width = max_size[0]
            height = round(max_size[0] / win_ratio)

        glfwSetWindowSize(window, width, height)

    glfwSetWindowSizeCallback(window, cbfun)

    cb_state = { "show_promt": True, "current": 0}
    glfwSetWindowUserPointer(window, cb_state)

    sketches = os.listdir(INPUT_DIR)
    sketches_display = [pathlib.Path(i).stem for i in sketches]

    def cbfun(window, key, scancode, action, mods):
        if key == GLFW_KEY_ENTER and action == GLFW_PRESS:
            glfwGetWindowUserPointer(window)["show_promt"] = False
        if key == GLFW_KEY_J and action == GLFW_PRESS:
            cb_state["current"] += 1
            if cb_state["current"] > len(sketches) - 1:
                cb_state["current"] = 0
        if key == GLFW_KEY_K and action == GLFW_PRESS:
            cb_state["current"] -= 1
            if cb_state["current"] < 0:
                cb_state["current"] = len(sketches) - 1

    glfwSetKeyCallback(window, cbfun)

    input_val = ""
    input_sketch = ""
    
    imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.0);
    #imgui.push_style_color(imgui.COLOR_BORDER, *RHUBARB_ACSENT);
    #imgui.push_style_color(imgui.COLOR_WINDOW_BACKGROUND, *RHUBARB_COLOUR);
    #imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, *RHUBARB_COLOUR, 0.5)
    #imgui.push_style_color(imgui.COLOR_TEXT, *RHUBARB_ACSENT)


    while not glfwWindowShouldClose(window) and cb_state["show_promt"]: 
        impl.process_inputs()
        imgui.new_frame()

        _sketch.draw()

        glUseProgram(program)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        imgui.set_next_window_size(*glfwGetWindowSize(window))
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_bg_alpha(0.0)

        imgui.begin("error", flags = imgui.WINDOW_NO_TITLE_BAR 
                                   | imgui.WINDOW_NO_RESIZE
                                   | imgui.WINDOW_NO_MOVE
                                   | imgui.WINDOW_NO_SCROLLBAR)
        imgui.push_item_width(glfwGetWindowSize(window)[0] * 0.2)
        imgui.set_cursor_pos((glfwGetWindowSize(window)[0] * 0.4, 
                              glfwGetWindowSize(window)[0] * 0.9))

        with imgui.font(cascadia_code):
            _, cb_state["current"] = imgui.combo("", cb_state["current"], sketches_display)
        imgui.pop_item_width()
        imgui.end()

        imgui.render()
        imgui.end_frame()
        impl.render(imgui.get_draw_data())

        glfwSwapBuffers(window)
        glfwPollEvents()

        sketch_path = INPUT_DIR + sketches[cb_state["current"]]

    imgui.pop_style_var()
    #imgui.pop_style_color()
    #imgui.pop_style_color()
    #imgui.pop_style_color()
    #imgui.pop_style_color()

    sketch_name = pathlib.Path(sketch_path).stem

    if not os.path.exists("images/" + sketch_name):
        os.mkdir("images/" + sketch_name)

    import configparser
    config = configparser.ConfigParser()
    config.read("rhubarb.ini")

    if not sketch_name in config.keys():
        config.add_section(sketch_name)
        config.set(sketch_name, "snapshot_count", "-1")
        config.set(sketch_name, "image_count", "-1")

    with open("rhubarb.ini", "w") as configfile:
        config.write(configfile)
    
    try:
        min_draw_time = update_sketch(open(sketch_path).read(), 
                                      _sketch, program)

    except Exception as e:
        min_draw_time = update_sketch(old_sketch_source, 
                                      _sketch, program) 
        error = parse_error(e)
        print(error)

    cb_state = { "paused": True, "snap_saved": False }
    glfwSetWindowUserPointer(window, cb_state)

    def cbfun(window, key, scancode, action, mods):
        state = glfwGetWindowUserPointer(window)

        if key == GLFW_KEY_SPACE and action == GLFW_PRESS:
            state["paused"] = not state["paused"]
        if key == GLFW_KEY_S and action == GLFW_PRESS:
            config = configparser.ConfigParser()
            config.read("rhubarb.ini")

            if not state["snap_saved"]:
                config[sketch_name]["snapshot_count"] = str(
                        int(config[sketch_name]["snapshot_count"]) + 1)

                config[sketch_name]["image_count"] = "-1"

                snapshot = open("snapshots/%s%s.py" % (
                        sketch_name, 
                        config[sketch_name]["snapshot_count"]), "x")
                snapshot.write(open(SKETCH_PATH).read())
                snapshot.close()
                state[1] = True

            config[sketch_name]["image_count"] = str(
                    int(config[sketch_name]["image_count"]) + 1)

            _sketch.target.save("images/%s/%s[%s.%s].png" % (
                sketch_name, 
                sketch_name, 
                config[sketch_name]["snapshot_count"],
                config[sketch_name]["image_count"]))

            with open("rhubarb.ini", "w") as configfile:
                config.write(configfile)
        
    glfwSetKeyCallback(window, cbfun)

    glfwSetWindowSize(window, 1920, 1080)

    get_time = lambda f: os.stat(f).st_ctime
    prev_time = get_time(sketch_path)

    update_frame = 1

    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0.0);
        
    while not glfwWindowShouldClose(window):
        draw_timer = time.time()

        impl.process_inputs()
        imgui.new_frame()

        try:
            if Shader.frame.val % update_frame == 0:
                t = get_time(sketch_path)
                if t != prev_time:
                    prev_time = t
                    _sketch.end()

                    old_sketch_source = open(SKETCH_PATH).read()
                    min_draw_time = update_sketch(open(sketch_path).read(), 
                                                  _sketch, program)
                    error = ""

                    cb_state["snap_saved"] = False

            if cb_state["paused"]: 
                _sketch.draw()

        except Exception as e:
            min_draw_time = update_sketch(old_sketch_source, 
                                          _sketch, program)
            _sketch.draw()
            error = parse_error(e)
            print(error)

        glUseProgram(program)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        if error:
            imgui.set_next_window_size(*glfwGetWindowSize(window))
            imgui.set_next_window_position(0, 0)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin("error", flags =
                          imgui.WINDOW_NO_TITLE_BAR 
                        | imgui.WINDOW_NO_RESIZE
                        | imgui.WINDOW_NO_MOVE
                        | imgui.WINDOW_NO_SCROLLBAR)

            with imgui.font(cascadia_code):
                imgui.text(error)

            imgui.end()

        imgui.render()
        imgui.end_frame()
        impl.render(imgui.get_draw_data())

        glfwSwapBuffers(window)
        glfwPollEvents()

        draw_time = time.time() - draw_timer
        wait_time = max(min_draw_time - (draw_time), 0.0)
        if cb_state["paused"]: Shader.time.val += draw_time + wait_time
        time.sleep(wait_time)

        Shader.frame.val += 1

        if _sketch.last_frame == Shader.frame.val: break
    
    imgui.pop_style_var()
    _sketch.end()
    glfwTerminate()

