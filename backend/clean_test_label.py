import cv2
import numpy as np


# Create a clean alcohol label for controlled testing
def create_test_label():
    # Create a large white image
    image = np.ones((1400, 1800, 3), dtype=np.uint8) * 255

    font = cv2.FONT_HERSHEY_SIMPLEX
    black = (0, 0, 0)

    # Main label information
    cv2.putText(
        image,
        "OLD TOM DISTILLERY",
        (100, 130),
        font,
        2,
        black,
        4
    )

    cv2.putText(
        image,
        "KENTUCKY STRAIGHT BOURBON WHISKEY",
        (100, 250),
        font,
        1.3,
        black,
        3
    )

    cv2.putText(
        image,
        "45% ALC./VOL.",
        (100, 360),
        font,
        1.5,
        black,
        3
    )

    cv2.putText(
        image,
        "750 mL",
        (100, 460),
        font,
        1.5,
        black,
        3
    )

    # Government warning heading
    cv2.putText(
        image,
        "GOVERNMENT WARNING:",
        (100, 620),
        font,
        1.4,
        black,
        5
    )

    # Government warning body
    warning_lines = [
        "(1) According to the Surgeon General, women should not drink",
        "alcoholic beverages during pregnancy because of the risk of",
        "birth defects.",
        "(2) Consumption of alcoholic beverages impairs your ability",
        "to drive a car or operate machinery, and may cause health",
        "problems."
    ]

    y = 720

    for line in warning_lines:
        cv2.putText(
            image,
            line,
            (100, y),
            font,
            0.9,
            black,
            2
        )

        y += 90

    cv2.imwrite(
        "test_images/clean_test_label.png",
        image
    )


create_test_label()

print("Created test_images/clean_test_label.png")