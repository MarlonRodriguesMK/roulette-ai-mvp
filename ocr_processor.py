import cv2
import pytesseract
import numpy as np
import re
from PIL import Image
import io

# ======================================================
# 🔹 PRÉ-PROCESSAMENTO AVANÇADO
# ======================================================
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    img = np.array(image)

    # 🔹 Aumenta resolução (prints costumam ser pequenos)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 🔹 Redução de ruído
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # 🔹 Binarização adaptativa (melhor que OTSU para apps)
    img = cv2.adaptiveThreshold(
        img, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )

    # 🔹 Dilatação leve para unir dígitos quebrados
    kernel = np.ones((2, 2), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)

    return img


# ======================================================
# 🔹 EXTRAÇÃO SEGURA DE NÚMEROS
# ======================================================
def extract_numbers(text: str) -> list[int]:
    """
    Extrai números válidos de roleta (0–36)
    Remove duplicações absurdas do OCR
    """
    found = re.findall(r"\b\d{1,2}\b", text)

    numbers = []
    for n in found:
        n = int(n)
        if 0 <= n <= 36:
            numbers.append(n)

    return numbers


# ======================================================
# 🔹 FUNÇÃO PRINCIPAL OCR
# ======================================================
def process_image(image_bytes: bytes) -> list[int]:
    processed_img = preprocess_image(image_bytes)

    # 🔹 OCR otimizado para linhas de números
    config = (
        "--oem 3 "
        "--psm 6 "
        "-c tessedit_char_whitelist=0123456789"
    )

    text = pytesseract.image_to_string(processed_img, config=config)

    numbers = extract_numbers(text)

    # 🔹 Remove leituras irreais (ex: OCR lixo)
    if len(numbers) < 3:
        return []

    return numbers
