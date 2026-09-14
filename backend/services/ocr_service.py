# File: ocr_service.py
# Date: 09/13/26
# Purpose: This file contains OCR functionality. Currently it takes an image, extracts text, sends it
#           through Tesseract OCR, and outputs the text. Eventually, this file will handle image uploads.


import cv2
import numpy as np
import pytesseract
from PIL import Image
from pytesseract import Output


# Prepare an image to make text easier for OCR to read
def preprocess_image(image: Image.Image) -> Image.Image:
    # Convert the Pillow image to an OpenCV array
    image_array = np.array(image)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    # Enlarge the image to help OCR read smaller text
    enlarged = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # Convert the image to high contrast black and white
    _, thresholded = cv2.threshold(
        enlarged,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return Image.fromarray(thresholded)


# Extract plain text from an image
def extract_text(image: Image.Image) -> str:
    processed_image = preprocess_image(image)

    text = pytesseract.image_to_string(processed_image)

    return text.strip()


# Extract OCR text along with word confidence scores
def extract_ocr_data(image: Image.Image):
    processed_image = preprocess_image(image)

    # Get individual OCR words and their confidence values
    data = pytesseract.image_to_data(
        processed_image,
        output_type=Output.DICT
    )

    words = []

    for index, text in enumerate(data["text"]):
        text = text.strip()

        if not text:
            continue

        confidence = float(data["conf"][index])

        words.append({
            "text": text,
            "confidence": confidence
        })

    # Calculate average confidence for recognized words
    valid_confidences = [
        word["confidence"]
        for word in words
        if word["confidence"] >= 0
    ]

    average_confidence = (
        sum(valid_confidences) / len(valid_confidences)
        if valid_confidences
        else 0
    )

    return {
        "words": words,
        "average_confidence": round(average_confidence, 2)
    }