"""Módulo de registro e inicialização de engines de OCR."""

from typing import Dict, Type, List

from ocr_pdf_cli.engines.base import OCREngine
from ocr_pdf_cli.engines.tesseract import TesseractEngine
from ocr_pdf_cli.engines.easyocr import EasyOCREngine
from ocr_pdf_cli.engines.paddleocr import PaddleOCREngine
from ocr_pdf_cli.engines.factory import (
    create_engine,
    supported_engines,
    available_engines,
    _ENGINE_REGISTRY,
)

# Dicionário legado para compatibilidade com código existente
ENGINES: Dict[str, Type[OCREngine]] = _ENGINE_REGISTRY


def get_engine(name: str) -> OCREngine:
    """Retorna uma nova instância da engine especificada pelo nome.

    Alias de compatibilidade para `create_engine()`.

    Args:
        name: O nome identificador da engine (ex: 'tesseract').

    Raises:
        ValueError: Se o nome da engine for desconhecido.

    Returns:
        Instância de OCREngine.
    """
    return create_engine(name)


__all__ = [
    "OCREngine",
    "TesseractEngine",
    "EasyOCREngine",
    "PaddleOCREngine",
    "ENGINES",
    "get_engine",
    "create_engine",
    "supported_engines",
    "available_engines",
]