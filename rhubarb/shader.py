from typing import Any
from OpenGL.GL import *
import math
import sys
from rhubarb.texture import Texture
from rhubarb.uniform import Uniform
from rhubarb.glsl import *
from rhubarb.constants import SKETCH_PATH

class GLSLCompileError(Exception):
    pass

class _Uniform:
    UPLOAD_FUN = {
        "float": glUniform1f, "int":   glUniform1i, "uint":  glUniform1ui,
        "vec2":  glUniform2f, "ivec2": glUniform2i, "uvec2": glUniform2ui,
        "vec3":  glUniform3f, "ivec3": glUniform3i, "uvec2": glUniform3ui,
        "vec4":  glUniform4f, "ivec4": glUniform4i, "uvec2": glUniform4ui
    }

    def __init__(self, glsl_type: str, name: str, val) -> None:
        self.name = name
        self.glsl_type = glsl_type
        self.val = val

        self.upload_funs = {}

    def init(self, shader) -> None:
        location = glGetUniformLocation(shader.id, self.name)
        fun = Uniform.UPLOAD_FUN[self.glsl_type]

        match(self.glsl_type):
            case "float" | "int" | "uint":
                def upload_fun(): fun(location, self.val)
            case "vec2" | "ivec2" | "uvec2" | \
                 "vec3" | "ivec3" | "uvec2" | \
                 "vec4" | "ivec4" | "uvec2":
                def upload_fun(): fun(location, *self.val)

        self.upload_funs[shader] = upload_fun
    
    def upload(self, shader):
        self.upload_funs[shader]()

class Shader:
    time = Uniform("float", "time", 0.0)
    frame = Uniform("int", "frame", 0)

    def __init__(self, source_code, num_invocations):
        """creates a GL compute shader which can be used to process data"""

        #self.textures = textures if type(textures) == tuple else (textures,)
        #self.uniforms = uniforms if type(uniforms) == tuple else (uniforms,)

        #self.uniforms = self.uniforms + (Shader.time, 
        #                                 Shader.frame)

        if type(num_invocations) == int: 
            num_invocations = (num_invocations,)

        match len(num_invocations):
            case 1: self.num_work_groups = (
                math.ceil(num_invocations[0] / 8),
                1,
                1)
            case 2: self.num_work_groups = (
                math.ceil(num_invocations[0] / 8),
                math.ceil(num_invocations[1] / 8),
                1)
            case 3: self.num_work_groups = (
                math.ceil(num_invocations[0] / 8),
                math.ceil(num_invocations[1] / 8),
                math.ceil(num_invocations[2] / 8))

        main = open(SKETCH_PATH).read()
        end = main.find(source_code)
        
        # TODO make this work

        if end == -1:
            line_num = 1
            #print("test")
        else:
            line_num = main[0:end].count("\n") + 1
            #print("test1")

        num_includes = source_code.count("#include")
        includes = ""

        for i in range(num_includes):
            start = source_code.find("#include")
            end = source_code.find("\n", start)

            path_start = source_code.find("<", start) + 1
            path_end = source_code.find(">", path_start)

            var = source_code[path_start:path_end]
            include = globals()[var]
            
            import rhubarb.glsl
            glsl_source = open(rhubarb.glsl.__file__).read()
            end = glsl_source.find(include)

            include_line_num = glsl_source[0:end].count("\n") + 1
           
            include = ("\n#line %i 1\n" % include_line_num 
            + include)
            
            includes += include

            source_code = source_code.replace(
                    source_code[start:path_end + 1], "")

        header = "#version 430\n"

        match len(num_invocations):
            case 1:
                header += "layout(local_size_x = 8, local_size_y = 1, local_size_z = 1) in;\n"
                header += "int num_invocations = %i;\n" % num_invocations
                header += "int id = int(gl_GlobalInvocationID.x);\n"
            case 2:
                header += "layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;\n"
                header += "ivec2 num_invocations = ivec2(%i, %i);\n" % num_invocations
                header += "ivec2 id = ivec2(gl_GlobalInvocationID.xy);\n"
            case 3:
                header += "layout(local_size_x = 8, local_size_y = 8, local_size_z = 8) in;\n"
                header += "ivec3 num_invocations = ivec3(%i, %i, %i);\n" % num_invocations
                header += "ivec3 id = ivec3(gl_GlobalInvocationID.xyz)\n;" 
    
        for texture in Texture.textures:
            header += "layout(rgba32f) uniform image%iD %s;\n" % (len(texture.size), texture.name)
            header += "uniform %s %s_size;\n" % (
                { 1: "int", 2: "ivec2", 3: "ivec3" }[len(texture.size)], texture.name)
            header += "uniform sampler%iD %s_sampler;\n" % (len(texture.size), texture.name)

        for uniform in Uniform.uniforms: 
            header += "uniform %s %s;\n" % (uniform.glsl_type, uniform.name)

        header += includes + "\n#line %i 0\n" % line_num
        source_code = header + source_code

        # compile and link shader for rendering
        shader = glCreateShader(GL_COMPUTE_SHADER)
        glShaderSource(shader, source_code)
        glCompileShader(shader)

        ok = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not ok:
            raise GLSLCompileError(glGetShaderInfoLog(shader).decode("utf-8")) 

        self.id = glCreateProgram()
        glAttachShader(self.id, shader)
        glDeleteShader(shader)

        glBindAttribLocation(self.id, 0, "vPosition")
        glLinkProgram(self.id)

        texture_uniforms = [
            _Uniform("int", Texture.textures[i].name, 
                    Texture.textures[i].unit) 
            for i in range(len(Texture.textures))]
        for uniform in texture_uniforms: uniform.init(self)

        size_uniforms = [
            _Uniform(
                { 1: "int", 2: "ivec2", 3: "ivec3" }
                        [len(Texture.textures[i].size)], 
                Texture.textures[i].name + "_size", 
                Texture.textures[i].size[0] 
                    if len(Texture.textures[i].size) == 1 
                    else Texture.textures[i].size
            )
            for i in range(len(Texture.textures))]
        for uniform in size_uniforms: uniform.init(self)

        sampler_uniforms = [
            _Uniform("int", Texture.textures[i].name + "_sampler", 
                    Texture.textures[i].unit)
            for i in range(len(Texture.textures))]
        for uniform in sampler_uniforms: uniform.init(self)
        
        glUseProgram(self.id)
        for uniform in texture_uniforms: uniform.upload(self)
        for uniform in size_uniforms:    uniform.upload(self)
        for uniform in sampler_uniforms: uniform.upload(self)

        for uniform in Uniform.uniforms: uniform.init(self)
    
    def dispatch(self) -> None:
        """dispatches shader"""
        glUseProgram(self.id)

        for uniform in Uniform.uniforms: uniform.upload(self)

        glDispatchCompute(*self.num_work_groups)
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

