import re


# Extract alcohol content even when OCR separates the percentage and ALC./VOL.
def extract_abv(text: str):
    # Find every percentage value in the OCR text
    percentages = list(re.finditer(r"\b(\d+(?:\.\d+)?)\s*%", text))

    # Find places where Tesseract recognized ALC./VOL.
    alcohol_markers = list(
        re.finditer(r"ALC\s*[./\\]*\s*VOL", text, re.IGNORECASE)
    )

    # Compare the position of each percentage to each alcohol marker
    for percentage in percentages:
        for marker in alcohol_markers:
            distance = abs(marker.start() - percentage.end())

            # Allow nearby OCR text or line breaks between the values
            if distance <= 60:
                return percentage.group(1) + "%"

    return None


# Extract common net content formats
def extract_net_contents(text: str):
    patterns = [
        r"\b\d+(?:\.\d+)?\s*mL\b",
        r"\b\d+(?:\.\d+)?\s*L\b",
        r"\b\d+(?:\.\d+)?\s*PINT\b",
        r"\b\d+(?:\.\d+)?\s*FL\.?\s*OZ\.?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0)

    return None


# Extract the government warning without keeping the rest of the label
def extract_government_warning(text: str):
    upper_text = text.upper()
    start = upper_text.find("GOVERNMENT WARNING")

    if start == -1:
        return None

    warning_text = text[start:]

    # Stop after the end of the standard warning when possible
    end_match = re.search(
        r"(?:health\s+)?(?:problems|oblems)\.",
        warning_text,
        re.IGNORECASE,
    )

    if end_match:
        return warning_text[:end_match.end()].strip()

    # Keep a limited section if OCR did not recognize the ending clearly
    return warning_text[:700].strip()


# Collect extracted label fields into one dictionary
def extract_fields(text: str):
    return {
        "alcohol_content": extract_abv(text),
        "net_contents": extract_net_contents(text),
        "government_warning": extract_government_warning(text),
    }