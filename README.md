# Screenshot to clipboard

[![tests](https://github.com/luke-gto/screenshot_OCR/actions/workflows/test.yml/badge.svg)](https://github.com/luke-gto/screenshot_OCR/actions/workflows/test.yml)

##### Next-gen Copy-Paste

This tiny script takes as input a rectangular region of the screen that contains some text and copies the recognized text to the clipboard.

### Installation

1) Install the dependencies listed in the `requirements.txt` file:

   ```
   pip install -r requirements.txt
   ```

2) Install the tesseract OCR engine from your distribution (for example `sudo apt install tesseract-ocr` or `sudo dnf install tesseract`).

3) Download the tesseract [trained model](https://github.com/tesseract-ocr/tessdata) for your language (for example `ita.traineddata`) and place it in the same directory as the script: the script points `TESSDATA_PREFIX` at its own folder.

4) On Linux the clipboard needs a backend binary: install `xclip` or `xsel` (for example `sudo apt install xclip`) or nothing will be pasted.

### Usage

```
python main.py --lang ita
```

- `--lang` is the tesseract language code of the text on screen (default `ita`, or set the `TESSERACT_LANG` environment variable).
- Select the region with two **left** clicks: one in the top left corner and one in the lower right one. The two clicks can be in any order.
- A right click cancels the selection; a selection smaller than a few pixels is rejected with a message.
- If no text is recognized the clipboard is left untouched and the script says so.
- Ctrl-V should paste the text after the OCR did its work.

The script is more useful if you can launch it through a shortcut.

### Tests

The offline suite stubs the display, the clipboard and tesseract, so it runs headless:

```
python tests/test_main.py
```

It also runs in CI on every push (see the badge above).

### Troubleshooting

- If `pip install` fails while building `evdev` (a pynput dependency), you are missing build headers: install the Python development headers and kernel headers (for example `sudo dnf install python3-devel kernel-headers` or `sudo apt install python3-dev linux-headers-generic`) and retry.
- If the script exits with "tesseract was not found", step 2 or 3 above is missing.

________________________________
**!!!**  It's only been tested on Linux with X11. **!!!**
