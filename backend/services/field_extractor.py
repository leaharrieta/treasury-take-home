import re


# Extract the alcohol percentage from common ALC./VOL. formats
def extract_abv(text: str):
    # First look for a percentage directly followed by ALC./VOL.
    abv_pattern = (
        r"\b(\d{1,2}(?:\.\d+)?)\s*%"
        r"\s*ALC\.?\s*[/\\]?\s*VOL\.?"
    )

    match = re.search(
        abv_pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1) + "%"

    # If OCR separated the text, find percentages and ALC./VOL. nearby
    percentages = list(
        re.finditer(
            r"\b(\d{1,2}(?:\.\d+)?)\s*%",
            text
        )
    )

    alcohol_markers = list(
        re.finditer(
            r"ALC\.?\s*[/\\]?\s*VOL\.?",
            text,
            re.IGNORECASE
        )
    )

    # Match a nearby percentage to the alcohol marker
    for percentage in percentages:
        for marker in alcohol_markers:
            distance = abs(
                marker.start() - percentage.end()
            )

            if distance <= 80:
                return percentage.group(1) + "%"

    return None


# Extract net contents using recognized measurement units
def extract_net_contents(text: str):
    # Match any numeric quantity followed by a supported unit
    pattern = (
        r"\b(\d+(?:\.\d+)?)\s*"
        r"(mL|L|PINTS?|PT|FL\.?\s*OZ\.?|"
        r"QUARTS?|QT|GALLONS?|GAL)\b"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    number = match.group(1)
    unit = match.group(2).upper()

    # Normalize the unit for consistent comparison
    if unit == "ML":
        unit = "mL"

    elif unit == "L":
        unit = "L"

    elif unit in {"PINT", "PT"}:
        unit = "PINT"

    elif unit == "PINTS":
        unit = "PINTS"

    elif unit.replace(".", "").replace(" ", "") == "FLOZ":
        unit = "FL. OZ."

    elif unit in {"QUART", "QT"}:
        unit = "QUART"

    elif unit == "QUARTS":
        unit = "QUARTS"

    elif unit in {"GALLON", "GAL"}:
        unit = "GALLON"

    elif unit == "GALLONS":
        unit = "GALLONS"

    return f"{number} {unit}"


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