import pyscreenshot as scrsh
import os
from pynput.mouse import Listener
import sys
from io import BytesIO
from PIL import Image
import pytesseract
import clipboard
import cv2
import numpy as np

os.environ["TESSDATA_PREFIX"] = os.path.dirname(os.path.realpath(__file__))

def pre_processing(image):
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    final_img = cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return final_img

def grab(x, y, w, h):
    im = scrsh.grab(bbox=(x, y, w, h))
    
    byte_io = BytesIO()
    im.save(byte_io, 'PNG')
    img = Image.open(BytesIO(byte_io.getvalue()))
    image_data = np.asarray(img)
    pre_processing(image_data)
    text = (pytesseract.image_to_string(img, lang='ita'))
    text = text.replace('\n', ' ')
    clipboard.copy(text)

click1 = 0
x1 = 0
y1 = 0

def on_click(x, y, button, pressed):
    global click1, x1, y1
    
    if pressed:
        if click1 == 0:
            x1 = x
            y1 = y
            click1 = 1
        else:
            grab(x1, y1, x, y)
            listener.stop()
            sys.exit()

with Listener(on_click=on_click) as listener:
    listener.join()