"""Configurações da aplicação."""

from pydantic import BaseModel, Field

class Settings(BaseModel):
    """Modelo de configurações da aplicação."""
    
    default_engine: str = Field(default="tesseract", description="Engine OCR padrão")
    default_language: str = Field(default="por", description="Idioma padrão para OCR")
    default_dpi: int = Field(default=300, description="DPI padrão para renderização de PDF")
    default_output_format: str = Field(default="pdf", description="Formato padrão de saída")
    verbose: bool = Field(default=False, description="Modo detalhado de logs")

settings = Settings()
