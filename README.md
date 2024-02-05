# Image to RGB565

## Description

PNG or GIF to RGB565 header file converter

## Commit

2024.02.05 - first commit  

## Test Spec

```text
Python 3.9.18
```  

## External Library

```text
rgb565-converter
opencv
```  

## Manual

```text
python converter.py --help

-h, --help          show this help message and exit

-i INPUT_FILE,    --input INPUT_FILE
                    Input file to be converted.
-o [OUTPUT_FILE], --output [OUTPUT_FILE]
                    Output file to be converted.
-r RESIZE,        --resize RESIZE
                    Resize image.
-d DELETE_TEMP,   --delete DELETE_TEMP
                    Delete temp image.
-s SWAP,          --swap SWAP 
                    Swap bytes for 16-bit words.
```  

```text
As a first example, if you want to convert gif/dev91.png to a header file while
resizing it at a 30% ratio, and delete the temp image file, run the following

python converter.py -i img/dev91.png -o dev91.h -r 0.3 -d true

As a second example, if you want to convert gif/duck.gif to a header file while
resizing it at a 50% ratio, and delete the temp image file, run the following


python converter.py -i gif/duck.gif -o duck_gif.h -r 0.5 -d true
```  

[Dev91 Blog](https://dev91.tistory.com/)
