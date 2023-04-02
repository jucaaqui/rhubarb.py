import glob
from OpenGL.GL import *
from PIL import Image, PngImagePlugin
import os
import math

class Texture:
    FORMAT = { "RGB": GL_RGB, "RGBA": GL_RGBA }

    textures = []

    def __init__(self, name: str, size: tuple, 
                 data: bytes = None, fmt = "RGB"):
        """creates a texture which can be accessed by shaders"""

        if type(size) == int: size = (size,)

        self.id = glGenTextures(1)
        self.name = name
        self.size = size
        self.unit = len(Texture.textures)
        self.target = { 
            1: GL_TEXTURE_1D, 
            2: GL_TEXTURE_2D, 
            3: GL_TEXTURE_3D 
        }[len(size)]
        self.upload_fun = { 
            1: glTexImage1D, 
            2: glTexImage2D, 
            3: glTexImage3D 
        }[len(self.size)]

        glActiveTexture({
            0: GL_TEXTURE0, 8:  GL_TEXTURE8, 
            1: GL_TEXTURE1, 9:  GL_TEXTURE9, 
            2: GL_TEXTURE2, 10: GL_TEXTURE10,
            3: GL_TEXTURE3, 11: GL_TEXTURE11,
            4: GL_TEXTURE4, 12: GL_TEXTURE12,
            5: GL_TEXTURE5, 13: GL_TEXTURE13,
            6: GL_TEXTURE6, 14: GL_TEXTURE14,
            7: GL_TEXTURE7, 15: GL_TEXTURE15 
        }[self.unit])
        glBindTexture(self.target, self.id)

        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.set_data(data, fmt)

        Texture.textures.append(self)

    def bind(self):
        glBindTexture(self.target, self.id)

    def get_data(self, fmt = "RGB") -> bytes:
        """returns a bytes of the data of the render target"""

        glBindTexture(self.target, self.id)
        data = glGetTexImage(self.target, 0, Texture.FORMAT[fmt], GL_UNSIGNED_BYTE)

        return data

    def set_data(self, data: bytes, fmt = "RGB") -> None:
        """uploads data to GL texture
        data e.g. : img.tobytes("raw", "RGBA", 0, 1)"""

        glBindTexture(self.target, self.id)
        self.upload_fun(self.target, 0, GL_RGBA32F, *self.size, 0, Texture.FORMAT[fmt], GL_UNSIGNED_BYTE, data)

        # is this line needed?
        glBindImageTexture(self.unit, self.id, 0, GL_TRUE, 0, GL_READ_WRITE, GL_RGBA32F)

    def save(self, path: str, source: str = "") -> None:
        """saves buffer as an image"""
        if self.target != GL_TEXTURE_2D:
            print("you can only save 2D textures!")
            return

        data = self.get_data("RGB")
        img = Image.frombytes("RGB", self.size, data)

        img.save(path, quality="maximum")

    def from_image(name: str, img: Image):
        return Texture(name, img.size,  
                       data=img.tobytes("raw", "RGBA", 0, 1), 
                       fmt="RGBA")

