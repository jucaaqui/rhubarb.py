from OpenGL.GL import *

class Uniform:
    uniforms = []

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

        Uniform.uniforms.append(self)

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





