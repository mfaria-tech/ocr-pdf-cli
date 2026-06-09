"""Módulo base para engines de OCR."""

from abc import ABC, abstractmethod
from typing import List
from PIL import Image
from ocr_pdf_cli.models.ocr_result import OCRResult

class OCREngine(ABC):
    """Classe base abstrata para todos os mecanismos (engines) de OCR."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome identificador da engine."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se a engine e seus executáveis/bibliotecas requeridos estão disponíveis no sistema."""
        pass

    @abstractmethod
    def extract_text(self, image: Image.Image, lang: str) -> str:
        """Extrai texto simples de uma imagem.

        Args:
            image: Objeto PIL Image representando a página.
            lang: Código do idioma a ser utilizado (ex: 'por', 'eng').

        Returns:
            Texto puro extraído da imagem.
        """
        pass

    @abstractmethod
    def extract_page(self, image: Image.Image, lang: str, page_number: int) -> OCRResult:
        """Realiza a extração estruturada de OCR contendo as palavras e coordenadas.

        Args:
            image: Objeto PIL Image representando a página.
            lang: Código do idioma a ser utilizado.
            page_number: Número da página associada.

        Returns:
            Um objeto OCRResult estruturado.
        """
        pass

    @abstractmethod
    def extract_document(self, images: List[Image.Image], lang: str) -> List[OCRResult]:
        """Processa uma lista de imagens de páginas gerando resultados de OCR para cada uma.

        Args:
            images: Lista de imagens PIL das páginas.
            lang: Código do idioma a ser utilizado.

        Returns:
            Lista de OCRResult correspondente às páginas.
        """
        pass
