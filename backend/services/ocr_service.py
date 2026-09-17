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


# Extract text, confidence, and word positions in one OCR pass
def extract_ocr_data(image):
    processed_image = preprocess_image(image)

    data = pytesseract.image_to_data(
        processed_image,
        output_type=Output.DICT
    )

    confidences = []
    lines = []
    current_line = []
    previous_line = None

    for index, word in enumerate(data["text"]):
        word = word.strip()

        if not word:
            continue

        # Save confidence for recognized words
        confidence = float(data["conf"][index])

        if confidence >= 0:
            confidences.append(confidence)

        # Tesseract gives every word a line number
        line_number = (
            data["block_num"][index],
            data["par_num"][index],
            data["line_num"][index]
        )

        # Start a new text line when the OCR line changes
        if previous_line is not None and line_number != previous_line:
            lines.append(" ".join(current_line))
            current_line = []

        current_line.append(word)
        previous_line = line_number

    # Add the final line
    if current_line:
        lines.append(" ".join(current_line))

    # Preserve line breaks for field extraction
    text = "\n".join(lines)

    if confidences:
        average_confidence = (
            sum(confidences) / len(confidences)
        )
    else:
        average_confidence = 0

    return {
        "text": text,
        "average_confidence": round(
            average_confidence,
            2
        ),
        "data": data,
        "ocr_image_size": processed_image.size
    }

# Run OCR using several image versions and combine the results
def extract_combined_text(image: Image.Image) -> str:
    results = []

    # Pass 1: original image
    original_text = pytesseract.image_to_string(image)
    results.append(original_text)

    # Convert image to OpenCV format
    image_array = np.array(image)

    # Pass 2: grayscale and enlarged
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    enlarged = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    gray_text = pytesseract.image_to_string(
        Image.fromarray(enlarged)
    )

    results.append(gray_text)

    # Pass 3: high contrast threshold
    _, thresholded = cv2.threshold(
        enlarged,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    threshold_text = pytesseract.image_to_string(
        Image.fromarray(thresholded)
    )

    results.append(threshold_text)

    # Combine all recognized text
    return "\n".join(results)