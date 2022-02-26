# Screenshot to clipboard

##### Next-gen Copy-Paste
 
This tiny script can take as input a rectangular region of the screen that contains some text and then copies it to the clipboard. 

### First installation

1) Install the dependecies listed in the ```requirements.txt``` file:

```pip install -r requirements.txt```

2) Download a tesseract [trained model](https://github.com/tesseract-ocr/tessdata) and place it in the same directory of the script.

3) Enjoy

The script is more useful if you can launch it through a shortcut.

### Usage

- You can select the region with two mouse clicks: the first in the top left corner and the second in the lower right one. 
- Ctrl-V should paste the text after the OCR did its work.

________________________________
**!!!**  It's only been tested on Linux with X11. **!!!**