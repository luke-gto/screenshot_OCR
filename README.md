# Screenshot to clipboard

##### Next-gen Copy-Paste

This tiny script takes as input a rectangular region of the screen that contains some text and copies the recognized text to the clipboard.

### Installation

1) Install the dependencies listed in the `requirements.txt` file:

   ```
   pip install -r requirements.txt
   ```

2) Install the tesseract OCR engine from your distribution (for example `sudo apt install tesseract-ocr` or `sudo dnf install tesseract`).

3) Download the tesseract [trained model](https://github.com/tesseract-ocr/tessdata) for your language (for example `ita.traineddata`) and place it in the same directory as the script: the script points `TESSDATA_PREFIX` at its own folder.

### Usage

```
python main.py --lang ita
```

- `--lang` is the tesseract language code of the text on screen (default `ita`, or set the `TESSERACT_LANG` environment variable).
- Select the region with two mouse clicks: one in the top left corner and one in the lower right one. The two clicks can be in any order.
- Ctrl-V should paste the text after the OCR did its work.

The script is more useful if you can launch it through a shortcut.

### Troubleshooting

- If `pip install` fails while building `evdev` (a pynput dependency), you are missing build headers: install the Python development headers and kernel headers (for example `sudo dnf install python3-devel kernel-headers` or `sudo apt install python3-dev linux-headers-generic`) and retry.

________________________________
**!!!**  It's only been tested on Linux with X11. **!!!**
