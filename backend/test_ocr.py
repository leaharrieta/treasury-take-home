# File: test_ocr.py
# Date: 09/13/26
# Purpose: To create a simple test label to prove Python to take in an image and output the text it sees.
#           I will use this to test if ocr_service.py works.


from PIL import Image

from services.ocr_service import extract_text
from services.field_extractor import extract_fields


# Load a real alcohol label image
image = Image.open("test_images/sample_label.png")

# Extract raw text using local OCR
text = extract_text(image)

print("OCR RESULT:")
print("--------------------")
print(text)


# Extract structured fields from the OCR text
fields = extract_fields(text)

print("\nEXTRACTED FIELDS:")
print("--------------------")
print(fields)