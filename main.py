"""Select a rectangular screen region and copy the text it contains to the clipboard.

Usage: python main.py [--lang ita]

Click the top left corner of the region, then the bottom right one (the two
clicks can be in any order). Tested on Linux with X11 only.
"""

import argparse
import os
import sys

import clipboard
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pynput.mouse import Button, Listener
import pyscreenshot as scrsh

os.environ["TESSDATA_PREFIX"] = os.path.dirname(os.path.realpath(__file__))

MIN_SELECTION_PIXELS = 4


def pre_processing(image):
    """Grayscale + Otsu threshold: black text on white background, binarized."""
    grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    final_img = cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return final_img


def ordered_corners(x1, y1, x2, y2):
    """Return (left, top, right, bottom) regardless of the click order."""
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def grab(x1, y1, x2, y2, lang):
    """OCR the selected region and return the recognized text, one line."""
    left, top, right, bottom = ordered_corners(x1, y1, x2, y2)
    im = scrsh.grab(bbox=(left, top, right, bottom))
    image_data = np.asarray(im)
    processed = pre_processing(image_data)
    text = pytesseract.image_to_string(Image.fromarray(processed), lang=lang)
    return text.replace("\n", " ").strip()


def main():
    parser = argparse.ArgumentParser(
        description="Copy the text inside a screen region to the clipboard."
    )
    parser.add_argument(
        "--lang",
        default=os.environ.get("TESSERACT_LANG", "ita"),
        help="tesseract language code, e.g. ita or eng (default: ita, "
        "or the TESSERACT_LANG environment variable)",
    )
    args = parser.parse_args()

    state = {"clicks": 0, "x1": 0, "y1": 0}

    def on_click(x, y, button, pressed):
        if not pressed:
            return
        if button != Button.left:
            listener.stop()
            sys.exit("Selection cancelled.")
        if state["clicks"] == 0:
            state["x1"], state["y1"] = x, y
            state["clicks"] = 1
            return
        left, top, right, bottom = ordered_corners(state["x1"], state["y1"], x, y)
        if (
            right - left < MIN_SELECTION_PIXELS
            or bottom - top < MIN_SELECTION_PIXELS
        ):
            listener.stop()
            sys.exit("Selection too small: click two distinct corners of a text region.")
        listener.stop()
        try:
            text = grab(state["x1"], state["y1"], x, y, args.lang)
        except pytesseract.TesseractNotFoundError:
            print(
                "tesseract was not found: install the OCR engine and download "
                "a trained model from https://github.com/tesseract-ocr/tessdata "
                "into this script's directory (see README).",
                file=sys.stderr,
            )
            sys.exit(1)
        if not text:
            sys.exit("No text recognized in the selection: clipboard left untouched.")
        clipboard.copy(text)
        sys.exit()

    with Listener(on_click=on_click) as listener:
        listener.join()


if __name__ == "__main__":
    main()
