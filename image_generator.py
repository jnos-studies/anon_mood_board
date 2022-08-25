from PIL import Image
# https://holypython.com/python-pil-tutorial/how-to-create-a-new-image-with-pil/

def make_mood_image (name, avg):
    new = Image.new(mode="RGB", size=(32,32), color=(avg[0], avg[1], avg[2]))
    new.save(f"static/mood_images/{name}.png")

make_mood_image("test",50)

