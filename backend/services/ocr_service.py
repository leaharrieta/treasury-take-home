# File: ocr_service.py
# Date: 09/13/26
# Purpose: This file contains OCR functionality. Currently it takes an image, extracts text, sends it
#           through Tesseract OCR, and outputs the text. Eventually, this file will handle image uploads.


from PIL import Image
import pytesseract

# Extract text from an image using local Tesseract OCR
def extract_text(image: Image.Image) -> str:
    # Send text through Tesseract OCR
    text = pytesseract.image_to_string(image)

    return text.strip()