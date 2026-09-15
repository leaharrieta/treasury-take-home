import time 
from io import BytesIO

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from services.field_extractor import (
    extract_fields,
    extract_government_warning
)
from services.ocr_service import (
    extract_combined_text,
    extract_ocr_data
)
from services.validator import validate_label


# FastAPI application
app = FastAPI()


# Return confirmation message
@app.get("/")
def home():
    return {"message": "Alcohol Label Verifier API is running"}


# Determine the overall result from all verification fields
def get_overall_status(results):
    statuses = [
        result["status"]
        for result in results.values()
    ]

    if "mismatch" in statuses:
        return "mismatch"

    if "needs_review" in statuses:
        return "needs_review"

    # If all fields match
    return "match"


# Verify an uploaded label against application information
@app.post("/verify")
async def verify_label(
    label_image: UploadFile = File(...),
    brand_name: str = Form(...),
    class_type: str = Form(...),
    alcohol_content: str = Form(...),
    net_contents: str = Form(...)
):
    allowed_types = ["image/jpeg", "image/png"]

    if label_image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Please upload a JPG or PNG image."
        )

    try:
        # Read the uploaded image
        image_bytes = await label_image.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file could not be read as an image."
        )
    
    # Start measuring verification time
    start_time = time.perf_counter()

    # Read the label using multiple OCR passes
    ocr_text = extract_combined_text(image)

    # Get OCR confidence information
    ocr_data = extract_ocr_data(image)

    # Extract structured label fields
    label_fields = extract_fields(ocr_text)

    # Store the application values entered by the user
    application_data = {
        "brand_name": brand_name,
        "class_type": class_type,
        "alcohol_content": alcohol_content,
        "net_contents": net_contents
    }

    # Compare the application against the label
    results = validate_label(
    application_data,
    label_fields,
    ocr_text,
    ocr_data["average_confidence"]
    )

    # Determine the overall verification result
    overall_status = get_overall_status(results)

    # Calculate total processing time
    processing_time = round(
        time.perf_counter() - start_time, 2
    )

    return {
        "overall_status": overall_status,
        "processing_time_seconds": processing_time,
        "meets_5_second_target": processing_time <= 5,
        "ocr_confidence": ocr_data["average_confidence"],
        "extracted_fields": label_fields,
        "results": results
    }