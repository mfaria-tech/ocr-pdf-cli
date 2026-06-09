"""Módulo para pré-processamento de imagens."""

import logging
from PIL import Image, ImageOps

logger = logging.getLogger("ocr_pdf_cli")

class ImagePreprocessor:
    """Aplica transformações na imagem para melhorar os resultados de reconhecimento OCR."""

    def preprocess(
        self,
        image: Image.Image,
        grayscale: bool = True,
        binarize: bool = False,
        threshold: int = 127
    ) -> Image.Image:
        """Aplica transformações na imagem do documento.

        Args:
            image: Imagem PIL original.
            grayscale: Se True, converte a imagem para escala de cinza.
            binarize: Se True, aplica binarização (preto e branco puro).
            threshold: Valor do limiar para binarização (0-255).

        Returns:
            Imagem PIL pré-processada.
        """
        processed = image
        
        if grayscale:
            logger.debug("Convertendo imagem para escala de cinza")
            processed = ImageOps.grayscale(processed)
            
        if binarize:
            logger.debug(f"Aplicando binarização com threshold {threshold}")
            # Garante que a imagem esteja em escala de cinza antes da binarização
            if processed.mode != "L":
                processed = ImageOps.grayscale(processed)
            processed = processed.point(lambda p: 255 if p > threshold else 0, mode="1")
            
        return processed
