# ======================================================
# OCR_SERVICE.PY - Serviço de processamento OCR
# ======================================================

import cv2
import pytesseract
import numpy as np
import re
from PIL import Image
import io
import logging
from typing import List, Optional


logger = logging.getLogger(__name__)


class OCRService:
    """
    Serviço de extração de números via OCR
    Com tratamento robusto de erros e múltiplas estratégias
    """
    
    def __init__(self):
        self._verify_tesseract()
        logger.info("✅ OCRService inicializado")
    
    def _verify_tesseract(self):
        """Verifica se Tesseract está instalado"""
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.warning(
                f"⚠️  Tesseract não encontrado: {str(e)}. "
                "OCR pode não funcionar corretamente."
            )
    
    def process_image(self, image_bytes: bytes) -> List[int]:
        """
        Processa imagem e extrai números
        
        Args:
            image_bytes: Bytes da imagem
            
        Returns:
            Lista de números encontrados (0-36)
        """
        try:
            # Tentar múltiplas estratégias de processamento
            strategies = [
                self._strategy_basic,
                self._strategy_adaptive,
                self._strategy_bilateral,
            ]
            
            all_numbers = set()
            
            for strategy in strategies:
                try:
                    numbers = strategy(image_bytes)
                    all_numbers.update(numbers)
                except Exception as e:
                    logger.warning(f"Estratégia falhou: {strategy.__name__}: {str(e)}")
                    continue
            
            result = sorted(list(all_numbers))
            logger.info(f"✅ OCR extraiu {len(result)} números: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro no OCR: {str(e)}", exc_info=True)
            return []
    
    def _strategy_basic(self, image_bytes: bytes) -> List[int]:
        """Estratégia básica de OCR"""
        # Converter bytes para imagem
        image = Image.open(io.BytesIO(image_bytes)).convert("L")
        img = np.array(image)
        
        # Threshold simples
        _, img = cv2.threshold(
            img, 
            0, 
            255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # OCR
        config = "--psm 6 -c tessedit_char_whitelist=0123456789"
        text = pytesseract.image_to_string(img, config=config)
        
        return self._extract_valid_numbers(text)
    
    def _strategy_adaptive(self, image_bytes: bytes) -> List[int]:
        """Estratégia com threshold adaptativo"""
        image = Image.open(io.BytesIO(image_bytes)).convert("L")
        img = np.array(image)
        
        # Equalizar histograma
        img = cv2.equalizeHist(img)
        
        # Threshold adaptativo
        img = cv2.adaptiveThreshold(
            img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Remover ruído
        kernel = np.ones((2, 2), np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        
        # OCR
        config = "--psm 6 -c tessedit_char_whitelist=0123456789"
        text = pytesseract.image_to_string(img, config=config)
        
        return self._extract_valid_numbers(text)
    
    def _strategy_bilateral(self, image_bytes: bytes) -> List[int]:
        """Estratégia com filtro bilateral (preserva bordas)"""
        image = Image.open(io.BytesIO(image_bytes))
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Converter para grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Filtro bilateral (suaviza mas preserva bordas)
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Threshold
        _, thresh = cv2.threshold(
            filtered,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # OCR
        config = "--psm 6 -c tessedit_char_whitelist=0123456789"
        text = pytesseract.image_to_string(thresh, config=config)
        
        return self._extract_valid_numbers(text)
    
    def _extract_valid_numbers(self, text: str) -> List[int]:
        """
        Extrai números válidos (0-36) do texto
        
        Args:
            text: Texto extraído pelo OCR
            
        Returns:
            Lista de números válidos
        """
        # Encontrar todos os números de 1 ou 2 dígitos
        found = re.findall(r'\b\d{1,2}\b', text)
        
        # Filtrar apenas números válidos da roleta
        valid = []
        for num_str in found:
            try:
                num = int(num_str)
                if 0 <= num <= 36:
                    valid.append(num)
            except ValueError:
                continue
        
        return valid
    
    def validate_image(self, image_bytes: bytes) -> tuple[bool, Optional[str]]:
        """
        Valida se a imagem pode ser processada
        
        Returns:
            (válido, mensagem_erro)
        """
        try:
            # Verificar se é uma imagem válida
            image = Image.open(io.BytesIO(image_bytes))
            
            # Verificar dimensões mínimas
            if image.width < 50 or image.height < 50:
                return False, "Imagem muito pequena (mínimo 50x50 pixels)"
            
            # Verificar tamanho máximo (10MB)
            if len(image_bytes) > 10 * 1024 * 1024:
                return False, "Imagem muito grande (máximo 10MB)"
            
            return True, None
            
        except Exception as e:
            return False, f"Imagem inválida: {str(e)}"
    
    def process_image_with_validation(
        self, 
        image_bytes: bytes
    ) -> tuple[List[int], Optional[str]]:
        """
        Processa imagem com validação prévia
        
        Returns:
            (números_extraídos, erro)
        """
        # Validar
        valid, error = self.validate_image(image_bytes)
        if not valid:
            return [], error
        
        # Processar
        try:
            numbers = self.process_image(image_bytes)
            return numbers, None
        except Exception as e:
            return [], str(e)


# ======================================================
# FUNÇÃO AUXILIAR PARA TESTES
# ======================================================

def test_ocr_service():
    """Função de teste do OCR"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python ocr_service.py <caminho_da_imagem>")
        return
    
    image_path = sys.argv[1]
    
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    service = OCRService()
    numbers, error = service.process_image_with_validation(image_bytes)
    
    if error:
        print(f"❌ Erro: {error}")
    else:
        print(f"✅ Números extraídos: {numbers}")


if __name__ == "__main__":
    test_ocr_service()