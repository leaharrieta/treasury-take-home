# File: test_ocr.py
# Date: 09/13/26
# Purpose: To create a simple test label to prove Python to take in an image and output the text it sees.
#           I will use this to test if ocr_service.py works.


from PIL import Image
from services.validator import validate_label

from services.ocr_service import extract_text
from services.field_extractor import extract_fields
from services.ocr_service import extract_text, extract_ocr_data


# Load a real alcohol label image
image = Image.open("test_images/sample_label.png")

# Extract raw text using local OCR
text = extract_text(image)

# Extract structured fields from the OCR text
fields = extract_fields(text)

# Get OCR confidence information
ocr_data = extract_ocr_data(image)

print("\nOCR CONFIDENCE:")
print("--------------------")
print("Average confidence:", ocr_data["average_confidence"])

#print("\nLOW CONFIDENCE WORDS:")
#print("--------------------")

# Display words that Tesseract was uncertain about
'''for word in ocr_data["words"]:
    if word["confidence"] < 60:
        print(
            word["text"],
            "-",
            round(word["confidence"], 2)
        )
'''

# Simulate information entered from the application
application_data = {
    "brand_name": "YOUR TEST BRAND",
    "class_type": "YOUR TEST CLASS OR TYPE",
    "alcohol_content": "5%",
    "net_contents": "1 PINT"
}


# Compare application values with the extracted label values
results = validate_label(
    application_data,
    fields,
    text,
    ocr_data["average_confidence"]
)

print("\nVERIFICATION RESULTS:")
print("--------------------")

for field, result in results.items():
    print(field)
    print("Status:", result["status"])
    print("Message:", result["message"])
    print()