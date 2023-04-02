from rhubarb.texture import Texture
from PIL import Image

target = Texture.from_image("target", Image.open("/home/juca/projects/rhubarb/rhubarb/resources/rhubarb.jpg"))
#target = Texture("target", (100,100))
last_frame = None
window_size = None
max_fps = 24

def draw():
    pass

def end():
    pass
