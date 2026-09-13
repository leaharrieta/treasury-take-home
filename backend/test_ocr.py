# File: test_ocr.py
# Date: 09/13/26
# Purpose: To create a simple test label to prove Python to take in an image and output the text it sees.
#           I will use this to test if ocr_service.py works.


import cv2
from PIL import Image

from services.ocr_service import extract_text


# Create a simple test label image
def create_test_image():
    # Start with a blank image
    image = 255 * __import__("numpy").ones((700, 1200, 3), dtype="uint8")

    # Choose a font
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Populate brand
    cv2.putText(image, "OLD TOM DISTILLERY",
                (50, 100), font, 1.5, (0, 0, 0), 3)

    # Populae class/type
    cv2.putText(image, "KENTUCKY STRAIGHT BOURBON WHISKEY",
                (50, 200), font, 1.1, (0, 0, 0), 2)

    # Populate ABV
    cv2.putText(image, "45% ALC./VOL.",
                (50, 300), font, 0.5, (0, 0, 0), 3)

    # Populate net contents
    cv2.putText(image, "750 mL",
                (50, 400), font, 0.5, (0, 0, 0), 3)

    # Populate government warning
    cv2.putText(image, "GOVERNMENT WARNING:",
                (50, 500), font, 0.5, (0, 0, 0), 3)

    cv2.imwrite("test_label.png", image)

    return Image.open("test_label.png")


# Create the image and run local OCR
image = create_test_image()
text = extract_text(image)

print("OCR RESULT:")
print("--------------------")
print(text)