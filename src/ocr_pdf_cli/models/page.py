"""Modelo de página de documento."""

from typing import Optional
from pydantic import BaseModel, Field
from .ocr_result import OCRResult

class Page(BaseModel):
    """Representa uma página específica de um documento PDF."""
    
    page_number: int = Field(..., description="O número da página (1-indexed)")
    width: int = Field(..., description="Largura da página em pontos do PDF (normalmente 72 DPI)")
    height: int = Field(..., description="Altura da página em pontos do PDF")
    image_path: Optional[str] = Field(default=None, description="Caminho para o arquivo temporário de imagem da página")
    ocr_result: Optional[OCRResult] = Field(default=None, description="O resultado obtido da execução do OCR")
