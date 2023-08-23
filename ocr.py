# NOTES:
    # OCR on this image does not work very well even with cropping
    # TODO: Ask user for array of numbers corresponding to depths instead

import pytesseract
import cv2
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_config = r'--oem 3 --psm 6'

def getDepths (DATAFILE, x, y, w, h):

    x1, x2 = x, int(x+(w*2.8))    # Right and left bound
    y1, y2 = int(y*0.9), y+h     # Upper and bottom bound

    # read the image using OpenCV
    image = cv2.imread(DATAFILE)
    cropped_image = image[y1:y2, x1:x2]

    cv2.imwrite("Cropped Image.jpg", cropped_image)

    string = pytesseract.image_to_string(cropped_image, config=custom_config)
    number_pattern = r'\d+'
    numbers = re.findall(number_pattern, string)

    return numbers
