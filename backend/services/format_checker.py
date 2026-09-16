import cv2
import numpy as np
import pytesseract
from PIL import Image
from pytesseract import Output
from difflib import SequenceMatcher

from services.ocr_service import preprocess_image


# Measure how much of a word remains after slight erosion
def get_erosion_ratio(image, data, index):
    left = data["left"][index]
    top = data["top"][index]
    width = data["width"][index]
    height = data["height"][index]

    if width <= 0 or height <= 0:
        return 0

    # Crop the detected word
    crop = image.crop(
        (
            left,
            top,
            left + width,
            top + height
        )
    )

    crop_array = np.array(crop)

    # Convert color image to grayscale
    if len(crop_array.shape) == 3:
        crop_array = cv2.cvtColor(
            crop_array,
            cv2.COLOR_RGB2GRAY
        )

    # Make text white and background black
    _, binary = cv2.threshold(
        crop_array,
        127,
        255,
        cv2.THRESH_BINARY_INV
    )

    original_pixels = cv2.countNonZero(binary)

    if original_pixels == 0:
        return 0

    # Slightly erode the letter strokes
    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    eroded = cv2.erode(
        binary,
        kernel,
        iterations=1
    )

    remaining_pixels = cv2.countNonZero(eroded)

    return remaining_pixels / original_pixels


# Compare GOVERNMENT WARNING with the text directly after it
def check_warning_bold(image: Image.Image):
    # Use the original image to locate the warning heading
    data = pytesseract.image_to_data(
        image,
        output_type=Output.DICT
    )

    government_index = None
    warning_index = None

    # Find GOVERNMENT WARNING even if OCR makes a small spelling error
    for index, word in enumerate(data["text"]):
        clean_word = "".join(
            character
            for character in word.upper()
            if character.isalpha()
        )

        government_score = SequenceMatcher(
            None,
            clean_word,
            "GOVERNMENT"
        ).ratio()

        if government_score >= 0.70:
            government_index = index

            # Look for WARNING shortly after GOVERNMENT
            for next_index in range(
                index + 1,
                min(index + 4, len(data["text"]))
            ):
                next_word = "".join(
                    character
                    for character in data["text"][next_index].upper()
                    if character.isalpha()
                )

                warning_score = SequenceMatcher(
                    None,
                    next_word,
                    "WARNING"
                ).ratio()

                if warning_score >= 0.70:
                    warning_index = next_index
                    break

            if warning_index is not None:
                break

    if government_index is None or warning_index is None:
        return {
            "status": "needs_review",
            "message": "Government warning heading could not be located."
        }

    heading_ratios = [
        get_erosion_ratio(
            image,
            data,
            government_index
        ),
        get_erosion_ratio(
            image,
            data,
            warning_index
        )
    ]

    heading_ratio = sum(heading_ratios) / len(heading_ratios)

    body_ratios = []

    # Compare against the first useful words after the heading
    for index in range(warning_index + 1, len(data["text"])):
        word = data["text"][index].strip()

        if not word:
            continue

        letters = "".join(
            character
            for character in word
            if character.isalpha()
        )

        # Skip punctuation and tiny fragments
        if len(letters) < 4:
            continue

        confidence = float(data["conf"][index])

        if confidence < 60:
            continue

        body_ratios.append(
            get_erosion_ratio(
                image,
                data,
                index
            )
        )

        # Use a small nearby sample
        if len(body_ratios) >= 10:
            break

    if len(body_ratios) < 5:
        return {
            "status": "needs_review",
            "message": "Not enough warning-body text was found."
        }

    body_ratio = sum(body_ratios) / len(body_ratios)

    bold_ratio = heading_ratio / body_ratio

    # Clearly bold
    if bold_ratio >= 1.90:
        return {
            "status": "match",
            "message": "Government warning heading appears bold.",
            "bold_ratio": round(bold_ratio, 2)
        }

    # Clearly not bold
    if bold_ratio <= 1.75:
        return {
            "status": "mismatch",
            "message": "Government warning heading does not appear bold.",
            "bold_ratio": round(bold_ratio, 2)
        }

    # Borderline result
    return {
        "status": "needs_review",
        "message": "Government warning bold formatting is uncertain.",
        "bold_ratio": round(bold_ratio, 2)
    }