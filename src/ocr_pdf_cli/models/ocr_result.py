"""Modelos de resultado OCR."""

from typing import List, Optional
from pydantic import BaseModel, Field

class OCRWord(BaseModel):
    """Representa uma única palavra detectada por OCR, com sua posição e nível de confiança."""
    
    text: str = Field(..., description="O texto da palavra")
    left: int = Field(..., description="Posição X (pixel) do canto superior esquerdo")
    top: int = Field(..., description="Posição Y (pixel) do canto superior esquerdo")
    width: int = Field(..., description="Largura da palavra em pixels")
    height: int = Field(..., description="Altura da palavra em pixels")
    confidence: float = Field(..., description="Nível de confiança da detecção (0 a 100)")

class OCRResult(BaseModel):
    """Representa o resultado completo de OCR de uma página."""
    
    text: str = Field(..., description="Texto completo extraído da página")
    words: List[OCRWord] = Field(default_factory=list, description="Lista de palavras com suas coordenadas")
    confidence: Optional[float] = Field(default=None, description="Confiança geral média do OCR na página")
    language: str = Field(default="por", description="Idioma utilizado para processar o OCR")
