"""Módulo contendo os modelos de dados da aplicação."""

from .ocr_result import OCRWord, OCRResult
from .page import Page
from .document import Document

__all__ = ["OCRWord", "OCRResult", "Page", "Document"]