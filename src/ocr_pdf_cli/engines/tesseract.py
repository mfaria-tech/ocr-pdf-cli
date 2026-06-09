"""Engine OCR baseada em Tesseract."""

import logging
from typing import List
from PIL import Image
import pytesseract  # type: ignore

from ocr_pdf_cli.engines.base import OCREngine
from ocr_pdf_cli.models.ocr_result import OCRResult, OCRWord

logger = logging.getLogger("ocr_pdf_cli")

class TesseractEngine(OCREngine):
    """Engine OCR que utiliza o Tesseract local através do pytesseract."""

    @property
    def name(self) -> str:
        return "tesseract"

    @property
    def is_available(self) -> bool:
        try:
            # Tenta ler a versão do tesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            logger.debug("Tesseract não encontrado no sistema ou não configurado corretamente.")
            return False

    def extract_text(self, image: Image.Image, lang: str) -> str:
        if not self.is_available:
            raise RuntimeError("Tesseract OCR não está instalado ou disponível no PATH.")
        
        try:
            text = pytesseract.image_to_string(image, lang=lang)
            return str(text)
        except Exception as e:
            logger.error(f"Erro ao extrair texto com Tesseract: {e}")
            raise RuntimeError(f"Falha no processamento do Tesseract: {e}")

    def extract_page(self, image: Image.Image, lang: str, page_number: int) -> OCRResult:
        if not self.is_available:
            raise RuntimeError("Tesseract OCR não está instalado ou disponível no PATH.")

        try:
            # Extrai texto simples
            text = self.extract_text(image, lang=lang)
            
            # Obtém dados estruturados das palavras e posições
            # pytesseract.image_to_data retorna um dicionário se especificarmos Output.DICT
            data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            
            words: List[OCRWord] = []
            confidences: List[float] = []
            
            n_elements = len(data.get("level", []))
            for i in range(n_elements):
                # Nível 5 indica uma palavra em Tesseract
                word_text = str(data["text"][i]).strip()
                if not word_text:
                    continue
                
                try:
                    conf = float(data["conf"][i])
                except (ValueError, TypeError):
                    conf = 0.0
                
                # Ignorar blocos não textuais (-1 conf em tesseract)
                if conf < 0:
                    continue
                
                words.append(
                    OCRWord(
                        text=word_text,
                        left=int(data["left"][i]),
                        top=int(data["top"][i]),
                        width=int(data["width"][i]),
                        height=int(data["height"][i]),
                        confidence=conf,
                    )
                )
                confidences.append(conf)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text=text,
                words=words,
                confidence=avg_confidence,
                language=lang,
            )
        except Exception as e:
            logger.error(f"Erro ao obter dados detalhados do Tesseract: {e}")
            # Em caso de falha no detalhado, tenta retornar texto puro sem coordenadas
            try:
                text = self.extract_text(image, lang=lang)
                return OCRResult(text=text, words=[], confidence=0.0, language=lang)
            except Exception:
                raise RuntimeError(f"Falha total no processamento do Tesseract: {e}")

    def extract_document(self, images: List[Image.Image], lang: str) -> List[OCRResult]:
        results = []
        for idx, img in enumerate(images):
            results.append(self.extract_page(img, lang=lang, page_number=idx + 1))
        return results
