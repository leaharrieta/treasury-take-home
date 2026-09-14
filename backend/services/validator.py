import re
from difflib import SequenceMatcher


# Official TTB government warning text
REQUIRED_WARNING = (
    "GOVERNMENT WARNING: "
    "(1) According to the Surgeon General, women should not drink "
    "alcoholic beverages during pregnancy because of the risk of birth defects. "
    "(2) Consumption of alcoholic beverages impairs your ability to drive a car "
    "or operate machinery, and may cause health problems."
)


# Normalize simple text before comparing values
def normalize_text(value: str):
    if value is None:
        return None

    return " ".join(value.lower().split())


# Convert alcohol percentages to a numeric value
def normalize_abv(value: str):
    if value is None:
        return None

    match = re.search(r"\d+(?:\.\d+)?", value)

    if not match:
        return None

    return float(match.group())


# Normalize net contents for simple comparisons
def normalize_net_contents(value: str):
    if value is None:
        return None

    value = value.upper()
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# Normalize warning text while keeping wording comparable
def normalize_warning(value: str):
    if value is None:
        return None

    value = value.lower()

    # Remove punctuation introduced or lost during OCR
    value = re.sub(r"[^a-z0-9\s]", " ", value)

    # Remove extra spaces and line breaks
    return " ".join(value.split())


# Compare application ABV with label ABV
def validate_abv(application_value: str, label_value: str):
    expected = normalize_abv(application_value)
    detected = normalize_abv(label_value)

    if detected is None:
        return {
            "status": "needs_review",
            "message": "Alcohol content could not be reliably found on the label."
        }

    if expected == detected:
        return {
            "status": "match",
            "message": f"Label alcohol content matches application: {label_value}"
        }

    return {
        "status": "mismatch",
        "message": (
            f"Application: {application_value} | "
            f"Label: {label_value}"
        )
    }


# Compare application net contents with label net contents
def validate_net_contents(application_value: str, label_value: str):
    expected = normalize_net_contents(application_value)
    detected = normalize_net_contents(label_value)

    if detected is None:
        return {
            "status": "needs_review",
            "message": "Net contents could not be reliably found on the label."
        }

    if expected == detected:
        return {
            "status": "match",
            "message": f"Label net contents match application: {label_value}"
        }

    return {
        "status": "mismatch",
        "message": (
            f"Application: {application_value} | "
            f"Label: {label_value}"
        )
    }


# Check the government warning against the required TTB wording
def validate_government_warning(warning_text: str, ocr_confidence: float):
    if warning_text is None:
        return {
            "status": "needs_review",
            "message": "Government warning could not be reliably detected."
        }

    # Confirm the required heading was detected in uppercase
    heading_present = "GOVERNMENT WARNING" in warning_text

    expected = normalize_warning(REQUIRED_WARNING)
    detected = normalize_warning(warning_text)

    similarity = SequenceMatcher(
        None,
        expected,
        detected
    ).ratio()

    # Strong OCR result and very similar warning text
    if heading_present and similarity >= 0.90:
        return {
            "status": "match",
            "message": "Government warning wording was successfully verified.",
            "similarity": round(similarity, 2)
        }

    # Avoid declaring a violation when OCR itself is uncertain
    if ocr_confidence < 80 or similarity >= 0.70:
        return {
            "status": "needs_review",
            "message": "Government warning requires manual review due to OCR uncertainty.",
            "similarity": round(similarity, 2)
        }

    return {
        "status": "mismatch",
        "message": "Government warning does not match the required wording.",
        "similarity": round(similarity, 2)
    }


# Validate all currently supported label fields
def validate_label(application_data, label_fields, ocr_text, ocr_confidence):
    return {
        "brand_name": validate_text_field(
            "Brand name",
            application_data["brand_name"],
            ocr_text
        ),

        "class_type": validate_text_field(
            "Class / type",
            application_data["class_type"],
            ocr_text
        ),

        "alcohol_content": validate_abv(
            application_data["alcohol_content"],
            label_fields["alcohol_content"]
        ),

        "net_contents": validate_net_contents(
            application_data["net_contents"],
            label_fields["net_contents"]
        ),

        "government_warning": validate_government_warning(
            label_fields["government_warning"],
            ocr_confidence
        )
    }

# Clean text so capitalization and punctuation do not affect comparison
def normalize_match_text(value: str):
    if value is None:
        return ""

    value = value.lower()

    # Remove punctuation
    value = re.sub(r"[^a-z0-9\s]", "", value)

    # Remove extra spaces and line breaks
    return " ".join(value.split())


# Find how closely the application value appears in OCR text
def find_best_match(application_value: str, ocr_text: str):
    expected = normalize_match_text(application_value)

    # Split the expected value into individual words
    expected_words = expected.split()

    # Normalize the entire OCR result
    detected = normalize_match_text(ocr_text)
    detected_words = detected.split()

    matched_words = 0

    # Check whether each expected word has a close OCR match
    for expected_word in expected_words:
        best_score = 0

        for detected_word in detected_words:
            score = SequenceMatcher(
                None,
                expected_word,
                detected_word
            ).ratio()

            if score > best_score:
                best_score = score

        # Allow small OCR spelling mistakes
        if best_score >= 0.75:
            matched_words += 1

    if not expected_words:
        return 0

    return matched_words / len(expected_words)


# Validate brand name or class/type against OCR text
def validate_text_field(field_name: str, application_value: str, ocr_text: str):
    expected = normalize_match_text(application_value)
    full_text = normalize_match_text(ocr_text)

    # Exact normalized text appears in OCR output
    if expected in full_text:
        return {
            "status": "match",
            "message": f"{field_name} matches the application."
        }

    score = find_best_match(
        application_value,
        ocr_text
    )

    # Almost all expected words were recognized
    if score >= 0.90:
        return {
            "status": "match",
            "message": f"{field_name} matches the application."
        }

    # Some of the expected text was recognized
    if score >= 0.60:
        return {
            "status": "needs_review",
            "message": f"{field_name} may match but requires manual review."
        }

    return {
        "status": "mismatch",
        "message": f"{field_name} was not found on the label."
    }