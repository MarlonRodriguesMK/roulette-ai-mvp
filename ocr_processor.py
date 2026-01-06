import cv2
import pytesseract
import numpy as np
import re
from PIL import Image
import io

# ======================================================
# PRÉ-PROCESSAMENTO DA IMAGEM
# ======================================================
def preprocess_image(img: np.ndarray) -> np.ndarray:
    # Aumenta contraste
    img = cv2.equalizeHist(img)

    # Binarização adaptativa
    img = cv2.adaptiveThreshold(
        img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # Remove ruídos leves
    kernel = np.ones((2, 2), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    return img

# ======================================================
# RECORTE AUTOMÁTICO DO HISTÓRICO
# ======================================================
def crop_history_region(img: np.ndarray) -> np.ndarray:
    """
    Recorta a região inferior-central da imagem,
    onde geralmente fica o histórico da roleta.
    """
    h, w = img.shape

    y_start = int(h * 0.55)
    y_end = int(h * 0.95)

    x_start = int(w * 0.10)
    x_end = int(w * 0.90)

    return img[y_start:y_end, x_start:x_end]

# ======================================================
# EXTRAÇÃO DE NÚMEROS
# ======================================================
def extract_numbers(text: str) -> list[int]:
    found = re.findall(r"\b\d{1,2}\b", text)
    numbers = []

    for n in found:
        n = int(n)
        if 0 <= n <= 36:
            numbers.append(n)

    return numbers

# ======================================================
# FUNÇÃO PRINCIPAL (API)
# ======================================================
def process_image(image_bytes: bytes) -> list[int]:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("L")
        img = np.array(image)

        # Tenta OCR no recorte
        cropped = crop_history_region(img)
        processed = preprocess_image(cropped)

        config = "--psm 6 -c tessedit_char_whitelist=0123456789"
        text = pytesseract.image_to_string(processed, config=config)

        numbers = extract_numbers(text)

        # Fallback: tenta imagem inteira se recorte falhar
        if len(numbers) < 3:
            processed_full = preprocess_image(img)
            text_full = pytesseract.image_to_string(processed_full, config=config)
            numbers = extract_numbers(text_full)

        return numbers

    except Exception:
        # Nunca quebrar a API
        return []
