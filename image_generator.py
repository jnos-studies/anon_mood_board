from multiprocessing.dummy import Array
from PIL import Image
from wordcloud import WordCloud

import multidict as multidict
import numpy as np
import re
import matplotlib.pyplot as plt

def make_mood_image (name, rgb):
    if isinstance(rgb,list):
        new = Image.new(mode="RGB", size=(32,32), color=(rgb[0], rgb[1], rgb[2]))
        print("test")
        new.save(f"app/static/mood_images/{name}.png")
    else:
        return 1


# https://github.com/amueller/word_cloud/blob/master/examples/frequency.py
# for word cloud
def getFrequencyDictForText(sentence):
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}

    # making dict for counting frequencies
    for text in sentence.split(" "):
        if re.match("a|the|an|the|to|in|for|of|or|by|with|is|on|that|be", text):
            continue
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    for key in tmpDict:
        fullTermsDict.add(key, tmpDict[key])
    return fullTermsDict

def makeImage(name, text):
    wc = WordCloud(background_color="white", max_words=1000)
    # generate word cloud from frequency of word
    wc.generate_from_frequencies(text)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(name + ".png")
    
def make_word_cloud (name, data):
    data_text = ""
    for word in data:
        data_text += word["description"] + " "
    data_text.lower()
    makeImage(name, getFrequencyDictForText(data_text))

    
    
