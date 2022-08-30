from multiprocessing.dummy import Array
from PIL import Image
# https://holypython.com/python-pil-tutorial/how-to-create-a-new-image-with-pil/

def make_mood_image (name, rgb):
    if isinstance(rgb,list):
        new = Image.new(mode="RGB", size=(32,32), color=(rgb[0], rgb[1], rgb[2]))
        print("test")
        new.save(f"app/static/mood_images/{name}.png")
    else:
        return 1

