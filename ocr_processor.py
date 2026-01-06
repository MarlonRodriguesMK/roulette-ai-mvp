import cv2
import pytesseract
import numpy as np
import re
from PIL import Image
import io

# Se necessário no Railway (normalmente não)
# pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Pré-processa a imagem para melhorar a leitura do OCR
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    img = np.array(image)

    # Aumenta contraste
    img = cv2.equalizeHist(img)

    # Binarização
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Remove ruído
    kernel = np.ones((2, 2), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    return img


def extract_numbers(text: str) -> list[int]:
    """
    Extrai apenas números válidos de roleta (0–36)
    """
    found = re.findall(r"\b\d{1,2}\b", text)
    numbers = []

    for n in found:
        n = int(n)
        if 0 <= n <= 36:
            numbers.append(n)

    return numbers


def process_image(image_bytes: bytes) -> list[int]:
    """
    Função principal chamada pela API
    """
    processed_img = preprocess_image(image_bytes)

    config = "--psm 6 -c tessedit_char_whitelist=0123456789"
    text = pytesseract.image_to_string(processed_img, config=config)

    numbers = extract_numbers(text)

    return numbers
