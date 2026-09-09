"""Offline test suite for screenshot_OCR: python tests/test_main.py

Display, clipboard and OCR binaries are stubbed, so the suite runs
headless and without tesseract installed.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

# ---- stubs for display/clipboard/OCR deps, installed before importing main ----
captured = {}


class Button:
    left = "left"
    right = "right"


class FakeListener:
    def __init__(self, on_click=None):
        captured["on_click"] = on_click

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def stop(self):
        captured["stopped"] = True

    def join(self):
        pass


mouse = SimpleNamespace(Listener=FakeListener, Button=Button)
sys.modules["pynput"] = SimpleNamespace(mouse=mouse)
sys.modules["pynput.mouse"] = mouse

clipboard_mod = SimpleNamespace(copy=lambda text: captured.update(copied=text))
sys.modules["clipboard"] = clipboard_mod


def fake_grab(bbox=None):
    captured["bbox"] = bbox
    img = Image.new("RGB", (200, 100), "white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 40), "ciao mondo", fill="black")
    return img


sys.modules["pyscreenshot"] = SimpleNamespace(grab=fake_grab)

import pytesseract

FAKE: dict = {"ocr": lambda image, lang=None: "ciao mondo\n"}


def fake_image_to_string(image, lang=None):
    arr = np.asarray(image)
    captured.setdefault("ocr_calls", []).append(
        {"ndim": arr.ndim, "lang": lang}
    )
    return FAKE["ocr"](image, lang)


pytesseract.image_to_string = fake_image_to_string

import main


def reset():
    captured.clear()
    captured["ocr_calls"] = []
    FAKE["ocr"] = lambda image, lang=None: "ciao mondo\n"


def text_image():
    img = Image.new("RGB", (200, 100), "white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 40), "ciao mondo", fill="black")
    return img


def test_pre_processing():
    proc = main.pre_processing(np.asarray(text_image()))
    assert proc.ndim == 2, "preprocessed image must be 2D grayscale"
    assert set(np.unique(proc).tolist()) <= {0, 255}, "must be binarized"
    assert (proc == 0).sum() > 0, "text pixels must survive as dark"
    assert (proc == 255).sum() > (proc == 0).sum(), "background must dominate"
    assert proc[0, 0] == 255, "white background must stay white"


def test_ordered_corners():
    assert main.ordered_corners(90, 80, 10, 20) == (10, 20, 90, 80)
    assert main.ordered_corners(10, 20, 90, 80) == (10, 20, 90, 80)


def test_grab_uses_binarized_image_and_lang():
    reset()
    main.grab(150, 90, 10, 10, "eng")
    assert captured["bbox"] == (10, 10, 150, 90), captured["bbox"]
    assert captured["ocr_calls"][-1]["lang"] == "eng"
    assert captured["ocr_calls"][-1]["ndim"] == 2, (
        "OCR must receive the binarized image, not the raw RGB grab"
    )


def test_click_flow_copies_text():
    reset()
    sys.argv = ["main.py", "--lang", "ita"]
    main.main()
    captured["on_click"](100, 80, Button.left, True)
    try:
        captured["on_click"](20, 30, Button.left, True)
    except SystemExit as exc:
        assert exc.code in (None, 0), exc.code
    assert captured["bbox"] == (20, 30, 100, 80), captured["bbox"]
    assert captured["ocr_calls"][-1]["lang"] == "ita"
    assert captured["copied"] == "ciao mondo"
    assert captured["stopped"]


def test_default_lang_is_ita():
    reset()
    sys.argv = ["main.py"]
    main.main()
    captured["on_click"](1, 1, Button.left, True)
    try:
        captured["on_click"](60, 60, Button.left, True)
    except SystemExit as exc:
        assert exc.code in (None, 0), exc.code
    assert captured["ocr_calls"][-1]["lang"] == "ita"


def test_right_click_cancels():
    reset()
    sys.argv = ["main.py"]
    main.main()
    captured["on_click"](10, 10, Button.left, True)
    try:
        captured["on_click"](50, 50, Button.right, True)
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert "cancelled" in str(exc)
    assert "copied" not in captured


def test_too_small_selection():
    reset()
    sys.argv = ["main.py"]
    main.main()
    captured["on_click"](10, 10, Button.left, True)
    try:
        captured["on_click"](12, 11, Button.left, True)
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert "too small" in str(exc)
    assert "copied" not in captured


def test_empty_recognition_leaves_clipboard_untouched():
    reset()
    FAKE["ocr"] = lambda image, lang=None: "   \n "
    sys.argv = ["main.py"]
    main.main()
    captured["on_click"](10, 10, Button.left, True)
    try:
        captured["on_click"](90, 90, Button.left, True)
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert "No text recognized" in str(exc)
    assert "copied" not in captured


def test_missing_tesseract_is_a_friendly_error():
    reset()

    def raise_not_found(image, lang=None):
        raise pytesseract.TesseractNotFoundError()

    FAKE["ocr"] = raise_not_found
    sys.argv = ["main.py"]
    main.main()
    captured["on_click"](10, 10, Button.left, True)
    try:
        captured["on_click"](90, 90, Button.left, True)
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert exc.code == 1


if __name__ == "__main__":
    failures = 0
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            reset()
            try:
                func()
                print("PASS", name)
            except AssertionError as exc:
                failures += 1
                print("FAIL", name, exc)
    if failures:
        sys.exit("{} test(s) failed".format(failures))
    print("ALL TESTS PASSED")
