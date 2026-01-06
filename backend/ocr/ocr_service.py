import cv2
import pytesseract
import re

def extrair_numeros(path: str):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    texto = pytesseract.image_to_string(gray)
    numeros = re.findall(r'\b\d{1,2}\b', texto)

    return [int(n) for n in numeros if 0 <= int(n) <= 36]
