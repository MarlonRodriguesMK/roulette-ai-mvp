import cv2
import pytesseract
import numpy as np
import re
from PIL import Image
import io

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    img = np.array(image)
    img = cv2.equalizeHist(img)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    return img

def extract_numbers(text: str) -> list[int]:
    found = re.findall(r"\b\d{1,2}\b", text)
    return [int(n) for n in found if 0 <= int(n) <= 36]

def process_image(image_bytes: bytes) -> list[int]:
    processed_img = preprocess_image(image_bytes)
    config = "--psm 6 -c tessedit_char_whitelist=0123456789"
    text = pytesseract.image_to_string(processed_img, config=config)
    numbers = extract_numbers(text)
    return numbers
