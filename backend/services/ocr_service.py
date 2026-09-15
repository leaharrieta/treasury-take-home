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

# Extract the government warning from a focused image region
def extract_warning_data(image: Image.Image):
    processed_image = preprocess_image(image)

    # Get OCR words and their positions
    data = pytesseract.image_to_data(
        processed_image,
        output_type=Output.DICT
    )

    heading_index = None

    # Find the word GOVERNMENT
    for index, word in enumerate(data["text"]):
        clean_word = "".join(
            character
            for character in word.upper()
            if character.isalpha()
        )

        if clean_word == "GOVERNMENT":
            heading_index = index
            break

    # Warning heading was not detected
    if heading_index is None:
        return {
            "text": None,
            "confidence": 0
        }

    # Get the location of the warning heading
    x = data["left"][heading_index]
    y = data["top"][heading_index]

    image_width, image_height = processed_image.size

    # Make a focused crop around the warning area
    crop_width = int(image_width * 0.45)
    crop_height = int(image_height * 0.45)

    center_x = x

    left = max(0, center_x - crop_width // 2)
    top = max(0, y - 40)

    right = min(image_width, left + crop_width)
    bottom = min(image_height, top + crop_height)

    warning_crop = processed_image.crop(
        (left, top, right, bottom)
    )

    # OCR the warning as one text block
    warning_text = pytesseract.image_to_string(
        warning_crop,
        config="--psm 6"
    )

    # Get confidence values from the focused crop
    warning_data = pytesseract.image_to_data(
        warning_crop,
        config="--psm 6",
        output_type=Output.DICT
    )

    confidences = []

    for confidence in warning_data["conf"]:
        confidence = float(confidence)

        if confidence >= 0:
            confidences.append(confidence)

    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0
    )

    return {
        "text": warning_text.strip(),
        "confidence": round(average_confidence, 2)
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