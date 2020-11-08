import pyscreenshot as scrsh
import os
from pynput.mouse import Listener
import sys
import io
from io import BytesIO
from PIL import Image
import pytesseract
import clipboard
import cv2
import numpy as np

path = (os.path.dirname(os.path.realpath(__file__)))
os.environ["TESSDATA_PREFIX"] = path

def grab(x, y, w, h):
    im = scrsh.grab(bbox=(x, y, w, h))
    byte_io = BytesIO()
    im.save(byte_io, 'JPEG')
    img = Image.open(BytesIO(byte_io.getvalue()))
    text = (pytesseract.image_to_string(img, lang='ita'))
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